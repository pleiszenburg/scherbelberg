# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/nuke.py: Nuke a cluster

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
from .._core.const import PREFIX, TOKENVAR
from .._core.log import configure_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


async def _main(prefix, tokenvar):

    await Cluster.nuke(
        prefix=prefix,
        tokenvar=tokenvar,
    )


@click.command(short_help="nuke cluster")
@click.option("-p", "--prefix", default=PREFIX, type=str, show_default=True)
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
def nuke(prefix, tokenvar):

    configure_log()

    run(_main(prefix, tokenvar))
