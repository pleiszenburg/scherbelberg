#!/bin/bash

# SCHERBELBERG
# HPC cluster deployment and management for the Hetzner Cloud
#
# https://github.com/pleiszenburg/scherbelberg
#
#     src/scherbelberg/share/bootstrap_03.sh: Third stage node setup
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

# Prefix
PREFIX=$1
# Install location
FORGE=$HOME/forge
# Environment
ENVNAME=${PREFIX}env
# Python version
PYTHONVERSION=$(echo $2)

# Python-Installer, alternative: Miniforge3-Linux-x86_64.sh
INSTALLER=Mambaforge-Linux-x86_64.sh
# Required packages
PACKAGES=${HOME}/.${PREFIX}/requirements_conda.txt

# Load Conda-Forge-installer
wget -q https://github.com/conda-forge/miniforge/releases/latest/download/$INSTALLER
chmod +x $INSTALLER

# Install Conda-Forge, create and activate environment
./$INSTALLER -b -p $FORGE < /dev/null > /dev/null 2> /dev/null
rm $INSTALLER
source $FORGE/bin/activate
mamba create -q -y -n $ENVNAME --file=$PACKAGES python=$PYTHONVERSION < /dev/null > /dev/null 2> /dev/null
echo "source $FORGE/bin/activate;conda activate $ENVNAME" >> .bashrc
