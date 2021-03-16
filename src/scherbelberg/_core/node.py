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

from hcloud import Client
from hcloud.servers.client import BoundServer

from typeguard import typechecked

from .abc import NodeABC

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
    def bootstrap_nodes(cls, *nodes: NodeABC, log: logging.Logger = None):

        log.info('Bootstrapping nodes ...')

        for node in nodes:

            log.info(node.name)


    @classmethod
    def from_name(cls, name: str, client: Client, fn_private: str) -> NodeABC:

        return cls(
            server = client.servers.get_by_name(name = name),
            client = client,
            fn_private = fn_private,
        )
