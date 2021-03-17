# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/create.py: Create a cluster

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

from .._core.cluster import Cluster

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@click.command(short_help = "create cluster")
@click.option('-p', '--prefix', default = "cluster", type = str, show_default = True)
@click.option('-t', '--tokenvar', default = "HETZNER", type = str, show_default = True)
@click.option('-a', '--wait', default = 0.5, type = float, show_default = True)
@click.option('-s', '--scheduler', default = 'cx11', type = str, show_default = True)
@click.option('-w', '--worker', default = 'cx11', type = str, show_default = True)
@click.option('-i', '--image', default = 'ubuntu-20.04', type = str, show_default = True)
@click.option('-d', '--datacenter', default = 'fsn1-dc14', type = str, show_default = True)
@click.option('-n', '--workers', default = 1, type = int, show_default = True)
def create(prefix, tokenvar, wait, scheduler, worker, image, datacenter, workers):

    Cluster(
        prefix = prefix,
        tokenvar = tokenvar,
        wait = wait,
    ).create(
        scheduler = scheduler,
        worker = worker,
        image = image,
        datacenter = datacenter,
        workers = workers,
    )
