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

import logging
import os
from time import sleep

from hcloud import Client
from hcloud.servers.client import BoundServer

from typeguard import typechecked

from .abc import NodeABC, SSHConfigABC
from .command import Command
from .process import Process
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

        self._log = logging.getLogger(name = self.name)


    def get_sshconfig(self, user: str) -> SSHConfigABC:

        return SSHConfig(
            name = self.public_ip4,
            user = user,
            fn_private = self._fn_private,
        )


    def ping_ssh(self) -> bool:

        _, err, _, _ = Command.from_list([
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=5",
            "-o", "PubkeyAuthentication=no",
            "-o", "PasswordAuthentication=no",
            "-o", "KbdInteractiveAuthentication=no",
            "-o", "ChallengeResponseAuthentication=no",
            "-p", "22",
            self.public_ip4,
        ]).run(returncode = True)

        return "Host key verification failed" in err[0] # "Permission denied"?


    def update(self):

        self._server = self._client.servers.get_by_name(name = self.name)


    @property
    def name(self) -> str:

        return self._server.name


    @property
    def public_ip4(self) -> str:

        return self._server.public_net.ipv4.ip


    @property
    def private_ip4(self) -> str:

        assert len(self._server.private_net) == 1

        return self._server.private_net[0].ip


    @classmethod
    def wait_for_nodes_ssh(
        cls,
        *nodes: NodeABC,
        wait: float = None,
        log: logging.Logger = None,
    ):

        assert wait > 0.0

        log.info('Waiting for ssh on nodes ...')

        nodes = list(nodes)

        while True:

            nodes = [
                None if (
                    True if node is None else node.ping_ssh()
                ) else node
                for node in nodes
            ]

            down = len([item for item in nodes if item is not None])
            if down == 0:
                sleep(wait) # one extra
                log.info('Ssh is up on all nodes.')
                return

            log.info(f'Continue waiting, ssh on {down:d} out of {len(nodes):d} nodes missing ...')
            sleep(wait)


    @classmethod
    def bootstrap_nodes(
        cls,
        *nodes: NodeABC,
        prefix: str,
        wait: float = None,
        log: logging.Logger = None,
    ):

        assert wait > 0.0

        cls.wait_for_nodes_ssh(*nodes, wait = wait, log = log)

        Process.wait_for(
            comment = 'copy root files to nodes', log = log, wait = wait,
            procs = [
                Command.from_scp(
                    *[os.path.abspath(os.path.join(
                        os.path.dirname(__file__), '..', 'share', fn,
                    )) for fn in ('bootstrap_01.sh', 'bootstrap_02.sh', 'sshd_config.patch')],
                    target = '~/',
                    host = node.get_sshconfig(user = 'root'),
                ).launch()
                for node in nodes
            ],
        )

        for comment, procs, user, ssh_wait in (
            ('run first bootstrap script on nodes', ["bash", "bootstrap_01.sh"], 'root', False),
            ('reboot nodes', ["shutdown", "-r", "now", "||", "true"], 'root', True),
            ('run second bootstrap script on nodes', ["bash", "bootstrap_02.sh", prefix], 'root', True),
        ):

            Process.wait_for(
                comment = comment, log = log, wait = wait,
                procs = [
                    Command.from_list(procs).on_host(
                        host = node.get_sshconfig(user = user)
                    ).launch()
                    for node in nodes
                ],
            )

            if ssh_wait:
                cls.wait_for_nodes_ssh(*nodes, wait = wait, log = log)

        Process.wait_for(
            comment = 'copy user files to nodes', log = log, wait = wait,
            procs = [
                Command.from_scp(
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
                    host = node.get_sshconfig(user = f'{prefix:s}user'),
                ).launch()
                for node in nodes
            ],
        )

        Process.wait_for(
            comment = 'run user bootstrap script on nodes', log = log, wait = wait,
            procs = [
                Command.from_list([
                    "bash", "bootstrap_03.sh", prefix
                ]).on_host(
                    host = node.get_sshconfig(user = f'{prefix:s}user')
                ).launch()
                for node in nodes
            ],
        )


    @classmethod
    def bootstrap_dask(
        cls,
        *workers: NodeABC,
        scheduler: NodeABC,
        prefix: str,
        wait: float = None,
        log: logging.Logger = None,
    ):

        assert wait > 0.0

        cls.wait_for_nodes_ssh(scheduler, wait = wait, log = log)

        Process.wait_for(
            comment = 'start dask scheduler', log = log, wait = wait,
            procs = [
                Command.from_list(
                ["bash", "bootstrap_scheduler.sh", "9753"]
                ).on_host(
                    host = scheduler.get_sshconfig(user = f'{prefix:s}user')
                ).launch()
            ],
        )

        cls.wait_for_nodes_ssh(*workers, wait = wait, log = log)
        sleep(wait)

        Process.wait_for(
            comment = 'start dask workers', log = log, wait = wait,
            procs = [
                Command.from_list(
                ["bash", "bootstrap_worker.sh", scheduler.private_ip4, "9753", "9754"]
                ).on_host(
                    host = worker.get_sshconfig(user = f'{prefix:s}user')
                ).launch()
                for worker in workers
            ],
        )


    @classmethod
    def from_name(cls, name: str, client: Client, fn_private: str) -> NodeABC:

        return cls(
            server = client.servers.get_by_name(name = name),
            client = client,
            fn_private = fn_private,
        )
