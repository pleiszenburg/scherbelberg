# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/cluster_async.py: A cluster - async edition

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
from typing import Any, Dict, List, Union

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

from typeguard import typechecked

from .abc import ClusterABC, NodeABC
from .const import (
    DASK_IPC,
    DASK_DASH,
    PREFIX,
    TOKENVAR,
    WAIT,
    WORKERS,
    HETZNER_INSTANCE_TINY,
    HETZNER_IMAGE_UBUNTU,
    HETZNER_DATACENTER,
)
from .command import Command
from .node import Node

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Cluster(ClusterABC):
    """
    Defines a cluster of nodes.

    Mutable.
    """

    def __init__(
        self,
        client: Client,
        scheduler: NodeABC,
        workers: List[NodeABC],
        network: BoundNetwork,
        firewall: BoundFirewall,
        dask_ipc: int = DASK_IPC,
        dask_dash: int = DASK_DASH,
        prefix: str = PREFIX,
        wait: float = WAIT,
        log: Union[Logger, None] = None,
    ):

        assert len(workers) > 0

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10
        assert dask_ipc != dask_dash

        self._client = client
        self._scheduler = scheduler
        self._workers = workers
        self._network = network
        self._firewall = firewall

        self._dask_ipc = dask_ipc # port
        self._dask_dash = dask_dash # port

        self._prefix = prefix
        self._wait = wait
        self._log = getLogger(name = prefix) if log is None else log


    def __repr__(self) -> str:

        return f'<Cluster prefix="{self._prefix:s}" alive={str(self.alive):s} workers={len(self._workers):d} ipc={self._dask_ipc:d} dash={self._dask_dash:d}>'


    def get_client(self) -> Any:
        """
        Creates and returns a DaskClient object for the cluster
        """

        if not self.alive:
            raise SystemError('cluster is dead')

        from dask.distributed import Client as DaskClient

        return DaskClient(f'{self._scheduler.public_ip4:s}:{self._dask_ipc:d}')


    async def destroy(self):
        """
        Destroys a living cluster
        """

        if not self.alive:
            raise SystemError('cluster is dead')

        if os.path.exists(self._fn_private(self._prefix)):
            os.unlink(self._fn_private(self._prefix))
        if os.path.exists(self._fn_public(self._prefix)):
            os.unlink(self._fn_public(self._prefix))

        # TODO


    @property
    def alive(self) -> bool:

        return self._scheduler is not None


    @property
    def scheduler(self) -> NodeABC:

        return self._scheduler


    @property
    def workers(self) -> List[NodeABC]:

        return self._workers.copy()


    @classmethod
    def _fn_private(cls, prefix: str) -> str:
        """
        Path to private key file
        """

        return os.path.join(os.getcwd(), f'{prefix:s}.key')


    @classmethod
    def _fn_public(cls, prefix: str) -> str:
        """
        Path to public key file
        """

        return f'{cls._fn_private(prefix):s}.pub'


    @classmethod
    async def _create_firewall(
        cls,
        prefix: str,
        client: Client,
        dask_ipc: int,
        dask_dash: int,
    ) -> BoundFirewall:

        _ = client.firewalls.create(
            name = f'{prefix:s}-firewall',
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

        return client.firewalls.get_by_name(
            name = f'{prefix:s}-firewall',
        )


    @classmethod
    async def _create_network(
        cls,
        prefix: str,
        client: Client,
        ip_range: str,
    ) -> BoundNetwork:

        _ = client.networks.create(
            name = f'{prefix:s}-network',
            ip_range = ip_range,
            subnets = [NetworkSubnet(
                ip_range = ip_range,
                type = 'cloud',
                network_zone = 'eu-central',
            )],
        )

        return client.networks.get_by_name(
            name = f'{prefix:s}-network',
        )


    @classmethod
    async def _create_node(
        cls,
        prefix: str,
        client: Client,
        network: BoundNetwork,
        firewall: BoundFirewall,
        ssh_key: BoundSSHKey,
        wait: float,
        suffix: str,
        servertype: str,
        datacenter: str,
        image: str,
        ip: str,
        labels: Union[Dict[str, str], None] = None,
    ) -> NodeABC:

        name = f'{prefix:s}-node-{suffix:s}'

        _ = client.servers.create(
            name = name,
            server_type = ServerType(name = servertype),
            image = Image(name = image),
            datacenter = Datacenter(name = datacenter),
            ssh_keys = ssh_key,
            firewalls = [firewall],
            labels = labels,
        )

        while True:
            server = client.servers.get_by_name(name = name)
            if server.status == Server.STATUS_RUNNING:
                break
            await sleep(wait)

        server.attach_to_network(
            network = network,
            ip = ip,
        )

        node = await Node.from_name(
            name = name,
            client = client,
            fn_private = cls._fn_private(prefix),
        )

        # TODO bootstrap

        return node


    @classmethod
    async def _create_ssh_key(
        cls,
        prefix: str,
        client: Client,
    ) -> BoundSSHKey:

        if os.path.exists(cls._fn_private(prefix)):
            raise SystemError('ssh private key file already exists')
        if os.path.exists(cls._fn_public(prefix)):
            raise SystemError('ssh public key file already exists')

        _, _ = await Command.from_list([
            'ssh-keygen',
            '-f', cls._fn_private(prefix), # path to file
            '-P', '', # no password
            '-t', 'rsa', # RSA
            '-b', '4096', # bits for RSA
            '-C', f'{prefix:s}-key', # comment
        ]).run()

        with open(cls._fn_public(prefix), 'r', encoding = 'utf-8') as f:
            public = f.read()

        _ = client.ssh_keys.create(
            name = f'{prefix:s}-key',
            public_key = public,
        )

        return client.ssh_keys.get_by_name(
            name = f'{prefix:s}-key',
        )


    @classmethod
    async def from_new(
        cls,
        prefix: str = PREFIX,
        tokenvar: str = TOKENVAR,
        wait: float = WAIT,
        scheduler: str = HETZNER_INSTANCE_TINY,
        worker: str = HETZNER_INSTANCE_TINY,
        image: str = HETZNER_IMAGE_UBUNTU,
        datacenter: str = HETZNER_DATACENTER,
        workers: int = WORKERS,
        dask_ipc: int = DASK_IPC,
        dask_dash: int = DASK_DASH,
        log: Union[Logger, None] = None,
    ) -> ClusterABC:
        """
        Creates a new cluster
        """

        assert workers > 0

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10
        assert dask_ipc != dask_dash

        log = getLogger(name = prefix) if log is None else log

        log.info('Creating cloud client ...')
        client = Client(token = os.environ[tokenvar])

        log.info('Creating ssh key ...')
        ssh_key = await cls._create_ssh_key(prefix, client)

        log.info('Creating network ...')
        network = await cls._create_network(prefix, client, ip_range = '10.0.1.0/24')

        log.info('Creating firewall ...')
        firewall = await cls._create_firewall(prefix, client, dask_ipc, dask_dash)

        log.info('Creating nodes ...')
        nodes = await gather(
            self._create_node(),
            *[
                self._create_node()
                for idx in range(workers)
            ]
        )
        scheduler, workers = nodes[0], nodes[1:]

        # TODO bootstrap

        log.info('Successfully created new cluster.')
        return cls(
            client = client,
            scheduler = scheduler,
            workers = workers,
            network = network,
            firewall = firewall,
            dask_ipc = dask_ipc,
            dask_dash = dask_dash,
            prefix = prefix,
            wait = wait,
            log = log,
        )


    @classmethod
    async def from_existing(
        cls,
        prefix: str = PREFIX,
        tokenvar: str = TOKENVAR,
        wait: float = WAIT,
        log: Union[Logger, None] = None,
    ) -> ClusterABC:
        """
        Attaches to existing cluster
        """

        log = getLogger(name = prefix) if log is None else log

        log.info('Creating cloud client ...')
        client = Client(token = os.environ[tokenvar])

        # TODO

        log.info('Successfully attached to existing cluster.')
        return cls(
            client = client,

            prefix = prefix,
            wait = wait,
            log = log,
        )
