# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/catalog.py: List data centers and available types of servers

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

import click
from tabulate import tabulate

from .._core.catalog import (
    get_datacenters,
    get_servertypes,
)
from .._core.const import TOKENVAR
from .._core.log import configure_log

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@click.command(short_help="list data centers and available servers types")
@click.option("-t", "--tokenvar", default=TOKENVAR, type=str, show_default=True)
@click.option("-l", "--log_level", default=ERROR, type=int, show_default=True)
@click.argument("datacenter", nargs=1, required=False)
def catalog(
    tokenvar,
    log_level,
    datacenter,
):

    configure_log(log_level)

    if datacenter is None:

        table = run(get_datacenters(tokenvar = tokenvar))
        columns = (
            'name',
            'city',
            'country',
            'description',
            'latitude',
            'longitude',
            'network_zone',
            'location_name',
            'location_description',
        )
        table = [
            [row[column] for column in columns]
            for row in table
        ]
        click.echo(tabulate(
            table,
            headers=columns,
            tablefmt="github",
        ))

        return

    table = run(get_servertypes(datacenter = datacenter, tokenvar = tokenvar))
    columns = (
        'name',
        # 'description',
        'cores',
        'cpu_type',
        'memory',
        'disk',
        'storage_type',
        'price_hourly_net',
        'price_hourly_gross',
        'price_monthly_net',
        'price_monthly_gross',
        'deprecated',
    )
    table = [
        [row[column] for column in columns]
        for row in table
    ]
    click.echo(tabulate(
        table,
        headers=columns,
        tablefmt="github",
    ))
