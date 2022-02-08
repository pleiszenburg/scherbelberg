# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/catalog.py: List data centers and available types of servers

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

import os
from typing import Any, Dict, List, Optional

from hcloud import Client
from hcloud.server_types.client import ServerTypesClient
from hcloud.server_types.domain import ServerType

from hcloud.locations.client import LocationsClient
from hcloud.locations.domain import Location

from .const import TOKENVAR
from .debug import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
async def get_locations(tokenvar: str = TOKENVAR) -> List[Dict[str, Any]]:
    """
    Queries a list of data center locations.

    Args:
        tokenvar : Name of the environment variable holding the cloud API login token.
    Returns:
        Data center locations.
    """

    client = Client(token=os.environ[tokenvar])

    return [
        _parse_location(location.data_model)
        for location in LocationsClient(client).get_all()
    ]

@typechecked
async def get_servertypes(location: str = 'fsn1', tokenvar: str = TOKENVAR) -> List[Dict[str, Any]]:
    """
    Queries a list of server types plus their specifications and prices.

    Args:
        location : Name of data center location.
        tokenvar : Name of the environment variable holding the cloud API login token.
    Returns:
        Server types plus their specifications and prices.
    """

    client = Client(token=os.environ[tokenvar])

    servertypes = ServerTypesClient(client).get_all()

    servertypes = [_parse_model(servertype.data_model) for servertype in servertypes]

    servertypes = [_parse_prices(servertype, location = location) for servertype in servertypes]
    servertypes = [servertype for servertype in servertypes if servertype is not None]

    servertypes.sort(key = _sort_key)

    return servertypes

@typechecked
def _parse_location(location: Location) -> Dict[str, Any]:
    return {
        attr: getattr(location, attr)
        for attr in dir(location)
        if not attr.startswith('_') and attr not in ('from_dict', 'id', 'id_or_name')
    }

@typechecked
def _parse_model(model: ServerType) -> Dict[str, Any]:
    model = {
        attr: getattr(model, attr)
        for attr in dir(model)
        if not attr.startswith('_') and attr not in ('from_dict', 'id', 'id_or_name')
    }
    if model.get('deprecated', None) is None:
        model['deprecated'] = False
    return model

@typechecked
def _parse_prices(servertype: Dict[str, Any], location: str = 'fsn1') -> Optional[Dict[str, Any]]:
    prices = servertype.pop('prices')
    prices = {price['location']: price for price in prices if price['location'] == location}
    if location not in prices.keys():
        return None
    price = prices[location]
    price.pop('location')
    for price_type in ('price_hourly', 'price_monthly'):
        price.update({f'{price_type:s}_{k:s}': v  for k, v in price.pop(price_type).items()})
    servertype.update(price)
    return servertype

@typechecked
def _sort_key(servertype: Dict[str, Any]):

    return servertype['cpu_type'].ljust(100) + f"{servertype['cores']:05d}"
