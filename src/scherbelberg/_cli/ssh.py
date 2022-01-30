# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/ssh.py: ssh into cluster member

    Copyright (C) 2021-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from asyncio import run

import click
import os
import sys

from .._core.cluster import Cluster
from .._core.const import PREFIX, TOKENVAR, WAIT
from .._core.log import configure_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def _main(prefix, tokenvar, wait, hostname):

    cluster = await Cluster.from_existing(
        prefix=prefix,
        tokenvar=tokenvar,
        wait=wait,
    )

    nodes = {node.name.split("-node-")[1]: node for node in cluster.workers}
    nodes["scheduler"] = cluster.scheduler

    if hostname not in nodes.keys():
        print(
            f'"{hostname:s}" is unknown in cluster "{prefix:s}": '
            + ", ".join(nodes.keys())
        )
        sys.exit(1)

    dev_null = "\\\\.\\NUL" if sys.platform.startswith("win") else "/dev/null"

    host = await nodes[hostname].get_sshconfig(user=f"{prefix:s}user")
    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",  # TODO security
        "-o",
        f"UserKnownHostsFile={dev_null:s}",  # TODO security
        "-o",
        "ConnectTimeout=5",
        "-o",
        "Compression=yes" if host.compression else "Compression=no",
        "-p",
        f"{host.port:d}",
        "-c",
        host.cipher,
        "-i",
        host.fn_private,
        "-q",
        f"{host.user:s}@{host.name:s}",
    ]
    os.execvpe(cmd[0], cmd, os.environ)


@click.command(short_help="ssh into cluster member")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-a", "--wait", default=WAIT, type=float, show_default=True)
@click.argument("hostname", nargs=1, type=str)
def ssh(prefix, tokenvar, wait, hostname):

    configure_log()

    run(_main(prefix, tokenvar, wait, hostname))
