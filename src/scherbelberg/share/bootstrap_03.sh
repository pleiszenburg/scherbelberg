#!/bin/bash

# Python-Installer, alternativ: Miniforge3-Linux-x86_64.sh
INSTALLER=Mambaforge-Linux-x86_64.sh
# Installationsort
FORGE=$HOME/forge
# Relevante Pakete
PACKAGES=packages.txt
# Umgebung
ENVNAME=clusterenv
# Name des Screens
SCREENNAME=clusterscreen

# In Screen starten, falls noch keiner läuft
if [ -z "$STY" ]; then exec screen -dm -S $SCREENNAME /bin/bash "$0"; fi

# Conda-Forge-Installer beziehen
wget https://github.com/conda-forge/miniforge/releases/latest/download/$INSTALLER
chmod +x $INSTALLER

# Conda-Forge installieren, Umgebung erstellen, wechseln
./$INSTALLER -b -p $FORGE
rm $INSTALLER
source $FORGE/bin/activate
mamba create -y -n $ENVNAME --file=packages.txt python=3.8
conda activate $ENVNAME
echo "source $FORGE/bin/activate;conda activate $ENVNAME" >> .bashrc
