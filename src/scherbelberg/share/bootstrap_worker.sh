#!/bin/bash

# SCHERBELBERG
# HPC cluster deployment and management for the Hetzner Cloud
#
# https://github.com/pleiszenburg/scherbelberg
#
#     src/scherbelberg/share/bootstrap_worker.sh: Start worker
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

SCHEDULER=$1
PORT=$2
DASHPORT=$3
NANNY=$4
PREFIX=$5

dask-worker \
    --protocol tls \
    --tls-ca-file ${PREFIX}_ca.crt \
    --tls-cert ${PREFIX}_node.crt --tls-key ${PREFIX}_node.key \
    --dashboard-address $DASHPORT --nanny-port $NANNY \
    --worker-port $PORT \
    tls://$SCHEDULER:$PORT \
    > worker_out 2> worker_err < /dev/null &
