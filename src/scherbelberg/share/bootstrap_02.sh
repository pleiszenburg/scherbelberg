#!/bin/bash

# Benutzer
USERNAME=clusteruser

# Fehlende Software installieren
apt --yes --force-yes -q install screen glances build-essential python3-venv python3-dev

# Neuer Benutzer
adduser --disabled-password --gecos "" -q $USERNAME

# ssh-Schlüssel an Benutzer übertragen
cp -a .ssh /home/$USERNAME/
chown $USERNAME:$USERNAME /home/$USERNAME/.ssh /home/$USERNAME/.ssh/*
rm -r .ssh

# Benutzer sudo-Rechte geben, ohne Passwort
usermod -aG sudo $USERNAME
echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# ssh für Root und Passwörter abdichten
patch /etc/ssh/sshd_config sshd_config.patch
systemctl reload ssh
