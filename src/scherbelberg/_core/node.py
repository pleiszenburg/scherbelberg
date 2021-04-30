# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/node.py: Cluster nodes (servers)

    Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the BSD 3-Clause License
("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE
Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from asyncio import sleep
from logging import getLogger, Logger
import os
from typing import Dict, Union

from hcloud import Client
from hcloud.servers.client import BoundServer

from typeguard import typechecked

from .abc import NodeABC, SSHConfigABC
from .command import Command
from .sshconfig import SSHConfig

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Node(NodeABC):
    """
    Represents one node of the cluster, i.e. a server.

    Mutable.
    """

    def __init__(
        self,
        server: BoundServer,
        client: Client,
        fn_private: str,
        prefix: str,
        wait: float,
        log: Union[Logger, None] = None,
    ):

        self._log = getLogger(name = prefix) if log is None else log

        assert len(fn_private) > 0
        assert wait > 0

        self._server = server
        self._client = client
        self._fn_private = fn_private
        self._prefix = prefix
        self._wait = wait


    def __repr__(self) -> str:

        return f'<node name={self.name:s} public={self.public_ip4:s} private={self.private_ip4}>'


    def _l(self, msg: str) -> str:

        return f'[{self.suffix:s}] {msg:s}'


    async def get_sshconfig(self, user: str) -> SSHConfigABC:

        return SSHConfig(
            name = self.public_ip4,
            user = user,
            fn_private = self._fn_private,
        )


    async def ping_ssh(self, user: str) -> bool:

        _, _, status, _ = await Command.from_list(
            ["exit"]
        ).on_host(
            host = await self.get_sshconfig(user = user),
        ).run(returncode = True, timeout = 5, wait = self._wait)

        assert len(status) == 1
        status = status[0]

        return status == 0


    async def reboot(self):

        self._server.reboot()


    async def update(self):

        self._server = self._client.servers.get_by_name(name = self.name)


    async def bootstrap(self):

        await self.wait_for_ssh(user = 'root')

        self._log.info(self._l('Copying root files to node ...'))
        await Command.from_scp(
            *[os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'share', fn,
            )) for fn in (
                'bootstrap_01.sh',
                'bootstrap_02.sh',
                'sshd_config.patch',
            )],
            target = '~/',
            host = await self.get_sshconfig(user = 'root'),
        ).run(wait = self._wait)

        self._log.info(self._l('Runing first bootstrap script ...'))
        await Command.from_list(["bash", "bootstrap_01.sh"]).on_host(
            host = await self.get_sshconfig(user = 'root')
        ).run(wait = self._wait)

        self._log.info(self._l('Rebooting ...'))
        await self.reboot()
        await self.wait_for_ssh(user = 'root')

        self._log.info(self._l('Runing second bootstrap script ...'))
        await Command.from_list(["bash", "bootstrap_02.sh", self._prefix]).on_host(
            host = await self.get_sshconfig(user = 'root')
        ).run(wait = self._wait)
        await self.wait_for_ssh(user = f'{self._prefix:s}user')

        self._log.info(self._l('Copying user files to node ...'))
        await Command.from_scp(
            *[os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'share', fn,
            )) for fn in (
                'bootstrap_03.sh',
                'bootstrap_scheduler.sh',
                'bootstrap_worker.sh',
                'requirements_conda.txt',
                'requirements_pypi.txt',
            )],
            target = '~/',
            host = await self.get_sshconfig(user = f'{self._prefix:s}user'),
        ).run(wait = self._wait)

        self._log.info(self._l('Runing third (user) bootstrap script ...'))
        await Command.from_list(["bash", "bootstrap_03.sh", self._prefix]).on_host(
            host = await self.get_sshconfig(user = f'{self._prefix:s}user')
        ).run(wait = self._wait)

        self._log.info(self._l('Bootstrapping done.'))


    async def start_scheduler(self, dask_ipc: int, dask_dash: int):

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10

        await self.wait_for_ssh(user = f'{self._prefix:s}user')

        self._log.info(self._l('Staring dask scheduler ...'))

        await Command.from_list(
            ["bash", "-i", "bootstrap_scheduler.sh", f'{dask_ipc:d}', f'{dask_dash:d}']
        ).on_host(
            host = await self.get_sshconfig(user = f'{self._prefix:s}user')
        ).run(wait = self._wait)

        self._log.info(self._l('Dask scheduler started.'))


    async def start_worker(self, dask_ipc: int, dask_dash: int, scheduler_ip4: str):

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10

        await self.wait_for_ssh(user = f'{self._prefix:s}user')

        self._log.info(self._l('Staring dask worker ...'))

        await Command.from_list(
            ["bash", "-i", "bootstrap_worker.sh", scheduler_ip4, f'{dask_ipc:d}', f'{dask_dash:d}']
        ).on_host(
            host = await self.get_sshconfig(user = f'{self._prefix:s}user')
        ).run(wait = self._wait)

        self._log.info(self._l('Dask worker started.'))


    async def wait_for_ssh(self, user: str):

        self._log.info(self._l('[%s] Waiting for SSH ...'), user)

        while True:
            ssh_up = await self.ping_ssh(user)
            if ssh_up:
                break
            await sleep(self._wait)
            self._log.info(self._l('[%s] Continuing to wait for SSH ...'), user)

        self._log.info(self._l('[%s] SSH up.'), user)


    @property
    def name(self) -> str:

        return self._server.name


    @property
    def labels(self) -> Dict[str, str]:

        return self._server.labels.copy()


    @property
    def public_ip4(self) -> str:

        return self._server.public_net.ipv4.ip


    @property
    def private_ip4(self) -> str:

        assert len(self._server.private_net) == 1

        return self._server.private_net[0].ip


    @property
    def suffix(self) -> str:

        return self.name.split('-node-')[1]


    @classmethod
    async def from_async(cls, **kwargs) -> NodeABC:

        return cls(**kwargs)


    @classmethod
    async def from_name(
        cls,
        name: str,
        client: Client,
        fn_private: str,
        prefix: str,
        wait: float,
        log: Union[Logger, None] = None,
    ) -> NodeABC:

        return cls(
            server = client.servers.get_by_name(name = name),
            client = client,
            fn_private = fn_private,
            prefix = prefix,
            wait = wait,
            log = log,
        )
