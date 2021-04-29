# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/creator.py: Creates a cluster

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

from asyncio import gather, sleep
from logging import getLogger, Logger
import os
from typing import Dict, Union

from typeguard import typechecked

from hcloud import Client
from hcloud.datacenters.domain import Datacenter
from hcloud.firewalls.client import BoundFirewall
from hcloud.firewalls.domain import FirewallRule
from hcloud.images.domain import Image
from hcloud.networks.client import BoundNetwork
from hcloud.networks.domain import NetworkSubnet
from hcloud.servers.domain import Server
from hcloud.server_types.domain import ServerType
from hcloud.ssh_keys.client import BoundSSHKey

from .abc import CreatorABC, NodeABC
from .command import Command
from .const import (
    DASK_IPC,
    DASK_DASH,
    WAIT,
    WORKERS,
    HETZNER_INSTANCE_TINY,
    HETZNER_IMAGE_UBUNTU,
    HETZNER_DATACENTER,
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Creator(CreatorABC):
    """
    Creates a cluster of nodes.

    Mutable.
    """

    def __init__(
        self,
        client: Client,
        prefix: str,
        fn_public: str,
        fn_private: str,
        wait: float = WAIT,
        dask_ipc: int = DASK_IPC,
        dask_dash: int = DASK_DASH,
        scheduler: str = HETZNER_INSTANCE_TINY,
        worker: str = HETZNER_INSTANCE_TINY,
        image: str = HETZNER_IMAGE_UBUNTU,
        datacenter: str = HETZNER_DATACENTER,
        workers: int = WORKERS,
        log: Union[Logger, None] = None,
    ):

        assert workers > 0

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10
        assert dask_ipc != dask_dash

        self._client = client
        self._prefix = prefix
        self._fn_public = fn_public
        self._fn_private = fn_private
        self._wait = wait

        self._log = getLogger(name = prefix) if log is None else log

        self._ssh_key = await self._create_ssh_key()
        self._network = await self._create_network(ip_range = '10.0.1.0/24')
        self._firewall = await self._create_firewall(dask_ipc, dask_dash)

        self._log.info('Creating nodes ...')

        nodes = await gather(
            self._create_node(
                suffix = 'scheduler',
                servertype = scheduler,
                datacenter = datacenter,
                image = image,
                ip = '10.0.1.200',
                labels = {
                    "dask_ipc": str(dask_ipc),
                    "dask_dash": str(dask_dash),
                }
            ),
            *[
                self._create_node(
                    suffix = f'worker{node:03d}',
                    servertype = worker,
                    datacenter = datacenter,
                    image = image,
                    ip = f'10.0.1.{100+node:d}',
                )
                for node in range(workers)
            ]
        )
        self._scheduler, self._workers = nodes[0], nodes[1:]

        # TODO bootstrap

        self._log.info('Successfully created new cluster.')


    @property
    def scheduler(self) -> None:

        return self._scheduler


    @property
    def workers(self) -> None:

        return self._workers.copy()


    @property
    def network(self) -> None:

        return self._network


    @property
    def firewall(self) -> None:

        return self._firewall


    async def _create_firewall(self, dask_ipc: int, dask_dash: int) -> BoundFirewall:

        self._log.info('Creating firewall ...')

        _ = self._client.firewalls.create(
            name = f'{self._prefix:s}-firewall',
            rules = [
                FirewallRule(
                    direction = 'in',
                    protocol = protocol,
                    source_ips = ['0.0.0.0/0', '::/0'],
                    destination_ips = [],
                    port = port,
                )
                for protocol, port in (
                    ('tcp', '22'),
                    ('icmp', None),
                    ('tcp', f'{dask_ipc:d}'),
                    ('tcp', f'{dask_dash:d}'),
                )
            ],
        )

        return self._client.firewalls.get_by_name(
            name = f'{self._prefix:s}-firewall',
        )


    async def _create_network(self, ip_range: str) -> BoundNetwork:

        self._log.info('Creating network ...')

        _ = self._client.networks.create(
            name = f'{self._prefix:s}-network',
            ip_range = ip_range,
            subnets = [NetworkSubnet(
                ip_range = ip_range,
                type = 'cloud',
                network_zone = 'eu-central',
            )],
        )

        self._log.info('Getting handle on network ...')

        return self._client.networks.get_by_name(
            name = f'{self._prefix:s}-network',
        )


    async def _create_node(
        self,
        suffix: str,
        servertype: str,
        datacenter: str,
        image: str,
        ip: str,
        labels: Union[Dict[str, str], None] = None,
    ) -> NodeABC:

        name = f'{self._prefix:s}-node-{suffix:s}'

        self._log.info('Creating node %s ...', name)

        _ = self._client.servers.create(
            name = name,
            server_type = ServerType(name = servertype),
            image = Image(name = image),
            datacenter = Datacenter(name = datacenter),
            ssh_keys = self._ssh_key,
            firewalls = [self._firewall],
            labels = labels,
        )

        self._log.info('Waiting for node %s to become available ...', name)

        while True:
            server = self._client.servers.get_by_name(name = name)
            if server.status == Server.STATUS_RUNNING:
                break
            await sleep(self._wait)

        self._log.info('Attaching network to node %s ...', name)

        server.attach_to_network(
            network = self._network,
            ip = ip,
        )

        self._log.info('Bootstrapping node %s ...', name)

        node = await Node.from_name(
            name = name,
            client = self._client,
            fn_private = self._fn_private,
        )

        # TODO bootstrap

        return node


    async def _create_ssh_key(self) -> BoundSSHKey:

        self._log.info('Creating ssh key ...')

        if os.path.exists(self._fn_private):
            raise SystemError('ssh private key file already exists')
        if os.path.exists(self._fn_public):
            raise SystemError('ssh public key file already exists')

        _, _ = await Command.from_list([
            'ssh-keygen',
            '-f', self._fn_private, # path to file
            '-P', '', # no password
            '-t', 'rsa', # RSA
            '-b', '4096', # bits for RSA
            '-C', f'{self._prefix:s}-key', # comment
        ]).run()

        self._log.info('Uploading ssh key ...')

        with open(self._fn_public, 'r', encoding = 'utf-8') as f:
            public = f.read()

        _ = self._client.ssh_keys.create(
            name = f'{self._prefix:s}-key',
            public_key = public,
        )

        self._log.info('Getting handle on ssh key ...')

        return self._client.ssh_keys.get_by_name(
            name = f'{self._prefix:s}-key',
        )


    @classmethod
    async def from_async(cls, **kwargs) -> CreatorABC:

        return cls(**kwargs)
