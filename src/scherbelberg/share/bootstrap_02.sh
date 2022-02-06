#!/bin/bash

# SCHERBELBERG
# HPC cluster deployment and management for the Hetzner Cloud
#
# https://github.com/pleiszenburg/scherbelberg
#
#     src/scherbelberg/share/bootstrap_02.sh: Second stage node setup
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

# run as root

PREFIX=$1
USERNAME=${PREFIX}user

# install required software
apt --yes --force-yes -q install screen glances build-essential python3-venv python3-dev > /dev/null

# create new user
adduser --disabled-password --gecos "" -q $USERNAME

# allow lingering for user (services)
loginctl enable-linger $USERNAME

# provide user with ssh key, remove from root account
cp -a /root/.ssh /home/$USERNAME/
chown $USERNAME:$USERNAME /home/$USERNAME/.ssh /home/$USERNAME/.ssh/*
rm -r /root/.ssh

# allow user to use sudo without password
usermod -aG sudo $USERNAME
echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# disallow password and root logins via ssh
patch /etc/ssh/sshd_config /root/.$PREFIX/sshd_config.patch
systemctl reload ssh
