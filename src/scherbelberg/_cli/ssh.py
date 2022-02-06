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
from logging import ERROR
import os
import sys

import click

from .._core.cluster import (
    Cluster,
    ClusterSchedulerNotFound,
    ClusterWorkerNotFound,
    ClusterFirewallNotFound,
    ClusterNetworkNotFound,
)
from .._core.const import PREFIX, TOKENVAR, WAIT
from .._core.log import configure_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def _main(prefix, tokenvar, wait, hostname, command):

    try:
        cluster = await Cluster.from_existing(
            prefix=prefix,
            tokenvar=tokenvar,
            wait=wait,
        )
    except ClusterSchedulerNotFound:
        click.echo(
            "Cluster scheduler could not be found. Cluster likely does not exist.",
            err=True,
        )
        sys.exit(1)
    except (
        ClusterWorkerNotFound,
        ClusterFirewallNotFound,
        ClusterNetworkNotFound,
    ) as e:
        click.echo(
            f"Cluster component missing ({type(e).__name__:s}). Cluster likely needs to be nuked.",
            err=True,
        )
        sys.exit(1)

    nodes = {node.name.split("-node-")[1]: node for node in cluster.workers}
    nodes["scheduler"] = cluster.scheduler

    if hostname not in nodes.keys():
        click.echo(
            f'"{hostname:s}" is unknown in cluster "{prefix:s}": '
            + ", ".join(nodes.keys()),
            err=True,
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
    if len(command) > 0:
        cmd.append(command)

    os.execvpe(cmd[0], cmd, os.environ)


@click.command(short_help="ssh into cluster node")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-a", "--wait", default=WAIT, type=float, show_default=True)
@click.option("-l", "--log_level", default=ERROR, type=int, show_default=True)
@click.argument("hostname", nargs=1, type=str)
@click.argument("command", nargs=1, type=str, default="")
def ssh(prefix, tokenvar, wait, log_level, hostname, command):

    configure_log(log_level)

    run(_main(prefix, tokenvar, wait, hostname, command))
