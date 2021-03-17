# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/ssh.py: ssh into cluster member

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

import click
import os
import sys

from .._core.cluster import Cluster

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@click.command(short_help = "ssh into cluster member")
@click.option('-p', '--prefix', default = "cluster", type = str, show_default = True)
@click.option('-t', '--tokenvar', default = "HETZNER", type = str, show_default = True)
@click.option('-a', '--wait', default = 0.5, type = float, show_default = True)
@click.argument('hostname', nargs = 1, type = str)
def ssh(prefix, tokenvar, wait, hostname):

    cluster = Cluster(
        prefix = prefix,
        tokenvar = tokenvar,
        wait = wait,
    )
    cluster.load()

    nodes = {
        node.name.split('-node-')[1]: node
        for node in cluster.workers
    }
    nodes['scheduler'] = cluster.scheduler

    if hostname not in nodes.keys():
        print(f'"{hostname:s}" is unknown in cluster "{prefix:s}": ' + ', '.join(nodes.keys()))
        sys.exit(1)

    host = nodes[hostname].get_sshconfig(user = f'{prefix:s}user')
    ssh = [
        "ssh",
        "-o", "StrictHostKeyChecking=no", # TODO security
        "-o", "UserKnownHostsFile=/dev/null", # TODO security
        "-o", "ConnectTimeout=5",
        "-o", "Compression=yes" if host.compression else "Compression=no",
        "-p", f'{host.port:d}',
        "-c", host.cipher,
        "-i", host.fn_private,
        f'{host.user:s}@{host.name:s}',
    ]
    os.execvpe(ssh[0], ssh, os.environ)
