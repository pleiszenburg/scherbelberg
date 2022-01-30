# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/create.py: Create a cluster

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

from .._core.cluster import Cluster
from .._core.const import (
    DASK_IPC,
    DASK_DASH,
    DASK_NANNY,
    PREFIX,
    TOKENVAR,
    WAIT,
    WORKERS,
    HETZNER_INSTANCE_TINY,
    HETZNER_IMAGE_UBUNTU,
    HETZNER_DATACENTER,
)
from .._core.log import configure_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@click.command(short_help="create cluster")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-a", "--wait", default=WAIT, type=float, show_default=True)
@click.option(
    "-s", "--scheduler", default=HETZNER_INSTANCE_TINY, type=str, show_default=True
)
@click.option(
    "-w", "--worker", default=HETZNER_INSTANCE_TINY, type=str, show_default=True
)
@click.option(
    "-i", "--image", default=HETZNER_IMAGE_UBUNTU, type=str, show_default=True
)
@click.option(
    "-d", "--datacenter", default=HETZNER_DATACENTER, type=str, show_default=True
)
@click.option("-n", "--workers", default=WORKERS, type=int, show_default=True)
@click.option("-c", "--dask_ipc", default=DASK_IPC, type=int, show_default=True)
@click.option("-d", "--dask_dash", default=DASK_DASH, type=int, show_default=True)
@click.option("-e", "--dask_nanny", default=DASK_NANNY, type=int, show_default=True)
def create(
    prefix,
    tokenvar,
    wait,
    scheduler,
    worker,
    image,
    datacenter,
    workers,
    dask_ipc,
    dask_dash,
    dask_nanny,
):

    configure_log()

    run(
        Cluster.from_new(
            prefix=prefix,
            tokenvar=tokenvar,
            wait=wait,
            scheduler=scheduler,
            worker=worker,
            image=image,
            datacenter=datacenter,
            workers=workers,
            dask_ipc=dask_ipc,
            dask_dash=dask_dash,
            dask_nanny=dask_nanny,
        )
    )
