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
    DASK_NANNY,
    PREFIX,
    TOKENVAR,
    WAIT,
    HETZNER_DATACENTER,
    HETZNER_IMAGE_UBUNTU,
    HETZNER_INSTANCE_TINY,
    WORKERS,
)
from .creator import Creator
from .node import Node

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Cluster(ClusterABC):
    """
    Defines a cluster of nodes. Mutable.
    Use the asynchronous ``from_*`` classmethods to instantiate objects of this class.

    Args:
        client : A cloud-API client object.
        scheduler : A node running the Dask scheduler.
        workers : A list of nodes running Dask workers.
        network : A cloud-API network object.
        firewall : A cloud-API firewall object.
        dask_ipc : Port used for Dask's interprocess communication.
        dask_dash : Port used for Dask's dashboard.
        dask_nanny : Port used for Dask's nanny.
        prefix : Name of cluster, used as a prefix in names of every component.
        wait : Timeout in seconds before actions are repeated or exceptions are raised.
        log : Allows to pass custom logger objects. Defaults to scherbelberg's own default logger.
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
        dask_nanny: int = DASK_NANNY,
        prefix: str = PREFIX,
        wait: float = WAIT,
        log: Union[Logger, None] = None,
    ):

        assert len(workers) > 0

        assert dask_ipc >= 2**10
        assert dask_dash >= 2**10
        assert dask_nanny >= 2**10

        assert len({dask_ipc, dask_dash, dask_nanny}) == 3

        self._client = client
        self._scheduler = scheduler
        self._workers = workers
        self._network = network
        self._firewall = firewall

        self._dask_ipc = dask_ipc # port
        self._dask_dash = dask_dash # port
        self._dask_nanny = dask_nanny # port

        self._prefix = prefix
        self._wait = wait
        self._log = getLogger(name = prefix) if log is None else log


    def __repr__(self) -> str:
        """
        Interactive string representation
        """

        return f'<Cluster prefix="{self._prefix:s}" alive={str(self.alive):s} workers={len(self._workers):d} ipc={self._dask_ipc:d} dash={self._dask_dash:d} nanny={self._dask_nanny:d}>'


    async def get_client(self, asynchronous: bool = True) -> Any:
        """
        Creates and returns a client.

        Args:
            asynchronous : Specifies if the ``Client`` object runs in asynchronous mode.
        Returns:
            ``dask.distributed.Client`` object attached to the cluster.
        """

        if not self.alive:
            raise SystemError('cluster is dead')

        from dask.distributed import Client as DaskClient
        from distributed.security import Security

        security = Security(
            tls_ca_file = f'{self._prefix:s}_ca.crt',
            tls_client_cert = f'{self._prefix:s}_node.crt',
            tls_client_key = f'{self._prefix:s}_node.key',
            require_encryption = True,
        )

        return DaskClient(
            f'tls://{self._scheduler.public_ip4:s}:{self._dask_ipc:d}',
            security = security,
            asynchronous = asynchronous,
        )


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

        for suffix in ('ca.key', 'ca.crt', 'node.key', 'node.crt'):
            fn = os.path.join(os.getcwd(), f'{self._prefix:s}_{suffix:s}')
            if os.path.exists(fn):
                os.unlink(fn)

        self._log.info('Cluster %s destroyed.', self._prefix)


    @property
    def alive(self) -> bool:
        """
        Is cluster alive?
        """

        return self._scheduler is not None


    @property
    def dask_ipc(self) -> int:
        """
        Port used for Dask's interprocess communication
        """

        return self._dask_ipc


    @property
    def dask_dash(self) -> int:
        """
        Port used for Dask's dashboard
        """

        return self._dask_dash


    @property
    def dask_nanny(self) -> int:
        """
        Port used for Dask's nanny
        """

        return self._dask_nanny


    @property
    def scheduler(self) -> NodeABC:
        """
        A node running the Dask scheduler
        """

        if not self.alive:
            raise SystemError('cluster is dead')

        return self._scheduler


    @property
    def workers(self) -> List[NodeABC]:
        """
        A list of nodes running Dask workers
        """

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
        dask_nanny: int = DASK_NANNY,
        scheduler: str = HETZNER_INSTANCE_TINY,
        worker: str = HETZNER_INSTANCE_TINY,
        image: str = HETZNER_IMAGE_UBUNTU,
        datacenter: str = HETZNER_DATACENTER,
        workers: int = WORKERS,
        log: Union[Logger, None] = None,
    ) -> ClusterABC:
        """
        Creates a new cluster

        Args:
            prefix : Name of cluster, used as a prefix in names of every component.
            tokenvar : Name of the environment variable holding the cloud API login token.
            wait : Timeout in seconds before actions are repeated or exceptions are raised.
            dask_ipc : Port used for Dask's interprocess communication.
            dask_dash : Port used for Dask's dashboard.
            dask_nanny : Port used for Dask's nanny.
            scheduler : Compute instance type used for Dask scheduler.
            worker : Compute instance type used for Dask workers.
            image : Operating system image.
            datacenter : Target data center.
            workers : Number of workers in cluster.
            log : Allows to pass custom logger objects. Defaults to scherbelberg's own default logger.
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
            dask_nanny = dask_nanny,
            scheduler = scheduler,
            worker = worker,
            image = image,
            datacenter = datacenter,
            workers = workers,
            log = log,
        )

        return cls(
            client = client,
            scheduler = creator.scheduler,
            workers = creator.workers,
            network = creator.network,
            firewall = creator.firewall,
            dask_ipc = dask_ipc,
            dask_dash = dask_dash,
            dask_nanny = dask_nanny,
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
            dask_nanny = int(scheduler.labels["dask_nanny"]),
            prefix = prefix,
            wait = wait,
            log = log,
        )
