# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_cli/_main_.py: CLI auto-detection

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

import importlib
import os
import sys

import click

from .. import __version__

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def _add_commands(ctx):
    """auto-detects sub-commands"""
    for cmd in (
        item[:-3] if item.lower().endswith(".py") else item[:]
        for item in os.listdir(os.path.dirname(__file__))
        if not item.startswith("_")
    ):
        try:
            ctx.add_command(
                getattr(importlib.import_module("scherbelberg._cli.%s" % cmd), cmd)
            )
        except ModuleNotFoundError:
            continue


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True)
def cli(version):
    """HPC cluster deployment and management for the Hetzner Cloud"""

    if not version:
        return

    print(__version__)
    sys.exit()


_add_commands(cli)
