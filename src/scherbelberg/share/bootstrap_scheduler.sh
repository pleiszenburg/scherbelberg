#!/bin/bash

# SCHERBELBERG
# HPC cluster deployment and management for the Hetzner Cloud
#
# https://github.com/pleiszenburg/scherbelberg
#
#     src/scherbelberg/share/bootstrap_scheduler.sh: Start scheduler
#
#     Copyright (C) 2021-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the BSD 3-Clause License
# ("License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>

# run as user

PORT=$1
DASHPORT=$2
PREFIX=$3

dask-scheduler \
    --protocol tls \
    --tls-ca-file ${PREFIX}_ca.crt \
    --tls-cert ${PREFIX}_node.crt --tls-key ${PREFIX}_node.key \
    --port $PORT --dashboard-address $DASHPORT \
    > scheduler_out 2> scheduler_err < /dev/null &
