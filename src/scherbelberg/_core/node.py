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
from logging import getLogger
import os
from subprocess import TimeoutExpired
from typing import Dict

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

    def __init__(self, server: BoundServer, client: Client, fn_private: str):

        assert len(fn_private) > 0

        self._server = server
        self._client = client
        self._fn_private = fn_private

        self._log = getLogger(name = self.name)


    def __repr__(self) -> str:

        return f'<node name={self.name:s} public={self.public_ip4:s} private={self.private_ip4}>'


    async def get_sshconfig(self, user: str) -> SSHConfigABC:

        return SSHConfig(
            name = self.public_ip4,
            user = user,
            fn_private = self._fn_private,
        )


    async def ping_ssh(self, user: str) -> bool:

        try:

            _, _, status, _ = await Command.from_list(
                ["exit"]
            ).on_host(
                host = self.get_sshconfig(user = user),
            ).run(returncode = True, timeout = 5)

        except TimeoutExpired:

            return False

        assert len(status) == 1
        status = status[0]

        return status == 0


    async def reboot(self):

        self._server.reboot()


    async def update(self):

        self._server = self._client.servers.get_by_name(name = self.name)


    async def bootstrap(self, wait: float, prefix: str):

        await self.wait_for_ssh(wait = wait, user = 'root')

        self._log.info('Copying root files to node ...')
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
        ).run()

        self._log.info('Runing first bootstrap script ...')
        await Command.from_list(["bash", "bootstrap_01.sh"]).on_host(
            host = await self.get_sshconfig(user = 'root')
        ).run()

        self._log.info('Rebooting ...')
        await self.reboot()
        await self.wait_for_ssh(wait = wait, user = 'root')

        self._log.info('Runing second bootstrap script ...')
        await Command.from_list(["bash", "bootstrap_02.sh"]).on_host(
            host = await self.get_sshconfig(user = 'root')
        ).run()
        await self.wait_for_ssh(wait = wait, user = f'{prefix:s}user')

        self._log.info('Copying user files to node ...')
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
            host = await self.get_sshconfig(user = f'{prefix:s}user'),
        ).run()

        self._log.info('Runing third (user) bootstrap script ...')
        await Command.from_list([
            "bash", "bootstrap_03.sh", prefix
        ]).on_host(
            host = await self.get_sshconfig(user = f'{prefix:s}user')
        ).run()

        self._log.info('Bootstrapping done.')


    async def wait_for_ssh(self, wait: float, user: str):

        self._log.info('Waiting for SSH, user "%s" ...', user)

        while True:
            ssh_up = await self.ping_ssh(user)
            if ssh_up:
                break
            await sleep(wait)
            self._log.info('Continuing to wait for SSH, user "%s" ...', user)

        self._log.info('SSH is up.')


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


    @classmethod
    async def from_async(cls, **kwargs) -> NodeABC:

        return cls(**kwargs)


    @classmethod
    async def from_name(cls, name: str, client: Client, fn_private: str) -> NodeABC:

        return cls(
            server = client.servers.get_by_name(name = name),
            client = client,
            fn_private = fn_private,
        )
