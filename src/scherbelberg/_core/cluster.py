# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/cluster.py: A cluster

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

from logging import getLogger, Logger
import os
from typing import Any, List, Union

from hcloud import Client
from hcloud.firewalls.client import BoundFirewall
from hcloud.networks.client import BoundNetwork

from typeguard import typechecked

from .abc import ClusterABC, NodeABC
from .const import (
    DASK_IPC,
    DASK_DASH,
    PREFIX,
    TOKENVAR,
    WAIT,
)
from .creator import Creator
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


    async def get_client(self) -> Any:
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

        cats = [
            getattr(self._client, name)
            for name in (
                'servers',
                'networks',
                'ssh_keys',
                'firewalls',
            )
        ]

        for cat in cats:
            for item in cat.get_all():
                if not item.name.startswith(self._prefix):
                    self._log.warning('Not deleting %s ...', item.name)
                    continue
                self._log.info('Deleting %s ...', item.name)
                item.delete()

        self._client = None
        self._scheduler = None
        self._workers = None
        self._network = None
        self._firewall = None

        if os.path.exists(self._fn_private(self._prefix)):
            os.unlink(self._fn_private(self._prefix))
        if os.path.exists(self._fn_public(self._prefix)):
            os.unlink(self._fn_public(self._prefix))

        self._log.info('Cluster %s destroyed.', self._prefix)


    @property
    def alive(self) -> bool:

        return self._scheduler is not None


    @property
    def dask_ipc(self) -> int:

        return self._dask_ipc


    @property
    def dask_dash(self) -> int:

        return self._dask_dash


    @property
    def scheduler(self) -> NodeABC:

        if not self.alive:
            raise SystemError('cluster is dead')

        return self._scheduler


    @property
    def workers(self) -> List[NodeABC]:

        if not self.alive:
            raise SystemError('cluster is dead')

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
    async def from_new(
        cls,
        prefix: str = PREFIX,
        tokenvar: str = TOKENVAR,
        wait: float = WAIT,
        dask_ipc: int = DASK_IPC,
        dask_dash: int = DASK_DASH,
        log: Union[Logger, None] = None,
        **kwargs,
    ) -> ClusterABC:
        """
        Creates a new cluster
        """

        log = getLogger(name = prefix) if log is None else log

        log.info('Creating cloud client ...')
        client = Client(token = os.environ[tokenvar])

        creator = await Creator.from_async(
            client = client,
            prefix = prefix,
            fn_public = cls._fn_public(prefix),
            fn_private = cls._fn_private(prefix),
            wait = wait,
            dask_ipc = dask_ipc,
            dask_dash = dask_dash,
            log = log,
            **kwargs,
        )

        return cls(
            client = client,
            scheduler = creator.scheduler,
            workers = creator.workers,
            network = creator.network,
            firewall = creator.firewall,
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

        log.info('Getting handle on scheduler ...')
        scheduler = await Node.from_name(
            name = f'{prefix:s}-node-scheduler',
            client = client,
            fn_private = cls._fn_private(prefix),
            prefix = prefix,
            wait = wait,
            log = log,
        )

        log.info('Getting handles on workers ...')
        workers = [
            Node(
                server = server,
                client = client,
                fn_private = cls._fn_private(prefix),
                prefix = prefix,
                wait = wait,
                log = log,
            )
            for server in client.servers.get_all()
            if server.name.startswith(prefix) and '-node-worker' in server.name
        ]

        log.info('Getting handle on firewall ...')
        firewall = client.firewalls.get_by_name(
            name = f'{prefix:s}-firewall',
        )

        log.info('Getting handle on network ...')
        network = client.networks.get_by_name(
            name = f'{prefix:s}-network',
        )

        log.info('Successfully attached to existing cluster.')
        return cls(
            client = client,
            scheduler = scheduler,
            workers = workers,
            network = network,
            firewall = firewall,
            dask_ipc = int(scheduler.labels["dask_ipc"]),
            dask_dash = int(scheduler.labels["dask_dash"]),
            prefix = prefix,
            wait = wait,
            log = log,
        )
