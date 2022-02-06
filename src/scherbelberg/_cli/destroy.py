# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/destroy.py: Destroy a cluster

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


async def _main(prefix, tokenvar, wait):

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

    await cluster.destroy()


@click.command(short_help="destroy cluster")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-a", "--wait", default=WAIT, type=float, show_default=True)
@click.option("-l", "--log_level", default=ERROR, type=int, show_default=True)
def destroy(prefix, tokenvar, wait, log_level):

    configure_log(log_level)

    run(_main(prefix, tokenvar, wait))
