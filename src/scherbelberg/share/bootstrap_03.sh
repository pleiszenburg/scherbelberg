#!/bin/bash

# SCHERBELBERG
# HPC cluster deployment and management for the Hetzner Cloud
#
# https://github.com/pleiszenburg/scherbelberg
#
#     src/scherbelberg/share/bootstrap_03.sh: Third stage node setup
#
#     Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>
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

# Python-Installer, alternative: Miniforge3-Linux-x86_64.sh
INSTALLER=Mambaforge-Linux-x86_64.sh
# Install location
FORGE=$HOME/forge
# Required packages
PACKAGES=requirements_conda.txt
# Environment
ENVNAME=clusterenv
# Name of screen
SCREENNAME=clusterscreen

# Launch into screen if there is not one yet
if [ -z "$STY" ]; then exec screen -dm -S $SCREENNAME /bin/bash "$0"; fi

# Load Conda-Forge-installer
wget https://github.com/conda-forge/miniforge/releases/latest/download/$INSTALLER
chmod +x $INSTALLER

# Install Conda-Forge, create and activate environment
./$INSTALLER -b -p $FORGE
rm $INSTALLER
source $FORGE/bin/activate
mamba create -y -n $ENVNAME --file=packages.txt python=3.8
conda activate $ENVNAME
echo "source $FORGE/bin/activate;conda activate $ENVNAME" >> .bashrc
