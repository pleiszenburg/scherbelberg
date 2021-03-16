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


    def get_sshconfig(self, user: str = 'root') -> SSHConfigABC:

        return SSHConfig(
            name = self.public_ip4,
            user = user,
            fn_private = self._fn_private,
        )


    def ping_ssh(self) -> bool:

        out, err, status, _ = Command.from_list([
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

        return "Permission denied" in err[0] or "Host key verification failed" in err[0]


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
                None if (True if node is None else node.ping_ssh()) else node
                for node in nodes
            ]

            down = len([item for item in nodes if item is not None])
            if down == 0:
                log.info('Ssh is up on all nodes.')
                return

            log.info(f'Continue waiting, ssh on {down:d} out of {len(nodes):d} nodes missing ...')
            sleep(wait)


    @classmethod
    def bootstrap_nodes(
        cls,
        *nodes: NodeABC,
        wait: float = None,
        log: logging.Logger = None,
    ):

        assert wait > 0.0

        cls.wait_for_nodes_ssh(*nodes, wait = wait, log = log)

        Process.wait_for(
            comment = 'copy first bootstrap script to nodes',
            procs = [
                Command.from_scp(
                    source = os.path.abspath(os.path.join(
                        os.path.dirname(__file__), '..', 'share', 'bootstrap_01.sh',
                        )),
                    target = '/root/',
                    host = node.get_sshconfig(),
                ).launch()
                for node in nodes
            ],
            log = log,
            wait = wait,
        )


    @classmethod
    def from_name(cls, name: str, client: Client, fn_private: str) -> NodeABC:

        return cls(
            server = client.servers.get_by_name(name = name),
            client = client,
            fn_private = fn_private,
        )
