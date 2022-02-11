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

# Install location
FORGE=$HOME/forge

# Systemd service unit file
SERVICE=$(cat <<-END
[Unit]
Description=Dask Scheduler
After=syslog.target network.target

[Service]
Type=simple
WorkingDirectory=$HOME
User=${PREFIX}user
Environment="PATH=${FORGE}/envs/${PREFIX}env/bin:${PATH}"
ExecStart=${FORGE}/envs/${PREFIX}env/bin/python ${FORGE}/envs/${PREFIX}env/bin/dask-scheduler \
    --pid-file=$HOME/.${PREFIX}/scheduler.pid \
    --protocol tls \
    --tls-ca-file $HOME/.${PREFIX}/ca.pub \
    --tls-cert $HOME/.${PREFIX}/cert.pub --tls-key $HOME/.${PREFIX}/cert \
    --port $PORT --dashboard-address $DASHPORT
ExecStop=/bin/kill `/bin/cat $HOME/.${PREFIX}/scheduler.pid`

[Install]
WantedBy=default.target
END
)

# Write unit file
echo "$SERVICE" | sudo tee /etc/systemd/system/dask_scheduler.service > /dev/null

# Reload units, useful for debugging
sudo systemctl daemon-reload

# Start service
sudo systemctl start dask_scheduler
