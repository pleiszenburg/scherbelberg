# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/scp.py: scp from/to cluster member

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


async def _fix_path(path, prefix, nodes):

    path = path.replace("\\\\", "/").replace("\\", "/")  # Windows SCP path fix

    if ":" not in path:
        return path, None

    hostname, path = path.split(":", maxsplit=-1)

    if hostname not in nodes.keys():
        click.echo(
            f'"{hostname:s}" is unknown in cluster "{prefix:s}": '
            + ", ".join(nodes.keys()),
            err=True,
        )
        sys.exit(1)

    host = await nodes[hostname].get_sshconfig(user=f"{prefix:s}user")

    return f"{host.user:s}@{host.name:s}:{path:s}", host


async def _main(prefix, tokenvar, wait, verbose, source, target):

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

    source = [await _fix_path(path, prefix, nodes) for path in source]
    target = await _fix_path(target, prefix, nodes)

    source_hosts = {host for _, host in source}
    source = [path for path, _ in source]
    target, target_host = target

    if None in source_hosts:
        source_hosts.remove(None)

    if len(source_hosts) > 1:
        click.echo(
            "Can not copy data from multiple hosts.",
            err=True,
        )
        sys.exit(1)
    if target_host is None and len(source_hosts) == 0:
        click.echo(
            "No host provided.",
            err=True,
        )
        sys.exit(1)
    if target_host is not None and len(source_hosts) == 1:
        click.echo(
            "Can not copy data from one host to another",
            err=True,
        )
        sys.exit(1)

    host = target_host if target_host is not None else source_hosts.pop()

    dev_null = "\\\\.\\NUL" if sys.platform.startswith("win") else "/dev/null"

    cmd = [
        "scp",
        "-o",
        "StrictHostKeyChecking=no",  # TODO security
        "-o",
        f"UserKnownHostsFile={dev_null:s}",  # TODO security
        "-o",
        "ConnectTimeout=5",
        "-o",
        "Compression=yes" if host.compression else "Compression=no",
        "-P",  # instead of "p" like in `ssh`
        f"{host.port:d}",
        "-c",
        host.cipher,
        "-i",
        host.fn_private,
        "-q",
    ]
    if verbose:
        cmd.append("-v")
    cmd.extend(
        [
            *source,
            target,
        ]
    )

    os.execvpe(cmd[0], cmd, os.environ)


@click.command(short_help="scp from/to cluster node")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-a", "--wait", default=WAIT, type=float, show_default=True)
@click.option("-l", "--log_level", default=ERROR, type=int, show_default=True)
@click.option("-v", "--verbose", is_flag=True, show_default=True)
@click.argument("source", nargs=-1)
@click.argument("target", nargs=1)
def scp(prefix, tokenvar, wait, log_level, verbose, source, target):

    configure_log(log_level)

    run(_main(prefix, tokenvar, wait, verbose, source, target))
