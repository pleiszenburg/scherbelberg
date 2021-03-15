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

import logging
import os
from time import sleep

from hcloud import Client
from hcloud.datacenters.domain import Datacenter
from hcloud.firewalls.domain import FirewallRule
from hcloud.images.domain import Image
from hcloud.networks.domain import NetworkSubnet
from hcloud.servers.client import BoundServer
from hcloud.servers.domain import Server
from hcloud.server_types.domain import ServerType

from typeguard import typechecked

from .abc import ClusterABC
from .command import Command

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Cluster(ClusterABC):
    """
    Defines a cluster of nodes.

    Mutable.
    """

    def __init__(self, prefix: str = 'cluster', tokenvar: str = 'HETZNER',):

        self._client = Client(token = os.environ[tokenvar])
        logging.basicConfig(
            format = '%(name)s/%(levelname)s @ %(asctime)-15s: %(message)s',
            level = logging.INFO,
        )
        self._log = logging.getLogger(name = prefix)

        assert len(prefix) > 0
        self._prefix = prefix

        self._fn_private = os.path.join(os.getcwd(), f'{self._prefix:s}.key')
        self._fn_public = f'{self._fn_private:s}.pub'

        self._public = None

        self._ssh_key = None
        self._network = None
        self._firewall = None

        self._scheduler = None
        self._workers = []


    def create(
        self,
        scheduler: str = 'cx11',
        worker: str = 'cx11',
        image: str = 'ubuntu-20.04',
        datacenter: str = 'fsn1-dc14',
        workers: int = 1,
    ):
        """
        Create new cluster
        """

        self._log.info('Creating ...')

        assert self._scheduler is None
        assert len(self._workers) == 0

        assert 0 < workers <= 100

        self._create_ssh_key()
        self._create_network(ip_range = '10.0.1.0/24')
        self._create_firewall()

        self._scheduler = self._create_node(
            suffix = 'scheduler',
            servertype = scheduler,
            datacenter = datacenter,
            image = image,
            ip = '10.0.1.200',
        )
        self._workers = [
            self._create_node(
                suffix = f'worker{node:03d}',
                servertype = worker,
                datacenter = datacenter,
                image = image,
                ip = f'10.0.1.{100+node:d}',
            )
            for node in range(workers)
        ]


    def load(self):
        """
        Load existing cluster
        """

        assert self._scheduler is None
        assert len(self._workers) == 0

        self._log.info('Loading ssh key ...')

        with open(self._fn_public, 'r') as f:
            self._public = f.read()

        self._log.info('Loading scheduler ...')

        self._scheduler = self._client.servers.get_by_name(f'{self._prefix:s}-node-scheduler')

        self._log.info('Loading workers ...')

        self._workers.extend([
            server
            for server in self._client.servers.get_all()
            if server.name.startswith(self._prefix) and '-node-worker' in server.name
        ])


    def destroy(self):
        """
        Destroy the entire cluster and all of its components
        """

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
                    continue
                self._log.info(f'Deleting {item.name:s} ...')
                item.delete()

        self._log.info('Deleting private key ...')
        if os.path.exists(self._fn_private):
            os.unlink(self._fn_private)

        self._log.info('Deleting public key ...')
        if os.path.exists(self._fn_public):
            os.unlink(self._fn_public)

        self._public = None

        self._ssh_key = None
        self._firewall = None
        self._network = None

        self._scheduler = None
        self._workers.clear()


    def _create_firewall(self):

        self._log.info('Creating firewall ...')

        _ = self._client.firewalls.create(
            name = f'{self._prefix:s}-firewall',
            rules = [
                FirewallRule(
                    direction = 'in',
                    protocol = 'tcp',
                    source_ips = ['0.0.0.0/0', '::/0'],
                    destination_ips = [],
                    port = '22',
                ),
                FirewallRule(
                    direction = 'in',
                    protocol = 'icmp',
                    source_ips = ['0.0.0.0/0', '::/0'],
                    destination_ips = [],
                ),
            ],
        )

        self._log.info('Handle on firewall ...')

        self._firewall = self._client.firewalls.get_by_name(
            name = f'{self._prefix:s}-firewall',
        )


    def _create_network(self, ip_range: str):

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

        self._log.info('Handle on network ...')

        self._network = self._client.networks.get_by_name(
            name = f'{self._prefix:s}-network',
        )


    def _create_node(self,
        suffix: str,
        servertype: str,
        datacenter: str,
        image: str,
        ip: str,
        wait: float = 0.25,
    ) -> BoundServer:

        name = f'{self._prefix:s}-node-{suffix:s}'

        self._log.info(f'Creating server {name:s} ...')

        _ = self._client.servers.create(
            name = name,
            server_type = ServerType(name = servertype),
            image = Image(name = image),
            datacenter = Datacenter(name = datacenter),
            ssh_keys = [self._ssh_key],
            firewalls = [self._firewall],
        )

        self._log.info(f'Waiting for server {name:s} to run ...')

        while True:
            server = self._client.servers.get_by_name(name = name)
            if server.status == Server.STATUS_RUNNING:
                break
            sleep(wait)

        server.attach_to_network(
            network = self._network,
            ip = ip,
        )

        self._log.info(f'Attaching network to server {name:s} ...')

        return self._client.servers.get_by_name(name = name)


    def _create_ssh_key(self):

        self._log.info('Creating ssh key ...')

        self._ssh_keygen()

        self._log.info('Uploading ssh key ...')

        _ = self._client.ssh_keys.create(
            name = f'{self._prefix:s}-key',
            public_key = self._public,
        )

        self._log.info('Handle on ssh key ...')

        self._ssh_key = self._client.ssh_keys.get_by_name(
            name = f'{self._prefix:s}-key',
        )


    def _ssh_keygen(self):

        if os.path.exists(self._fn_private):
            os.unlink(self._fn_private)
        if os.path.exists(self._fn_public):
            os.unlink(self._fn_public)

        out, err = Command.from_list([
            'ssh-keygen',
            '-f', self._fn_private, # path to file
            '-P', '', # no password
            '-t', 'rsa', # RSA
            '-b', '4096', # bits for RSA
            '-C', f'{self._prefix:s}-key', # comment
        ]).run()

        if len(out[0].strip()) > 0:
            self._log.info(out[0].strip())
        if len(err[0].strip()) > 0:
            self._log.error(err[0].strip())

        with open(self._fn_public, 'r') as f:
            self._public = f.read()
