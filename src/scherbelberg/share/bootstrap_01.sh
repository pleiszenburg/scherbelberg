#!/bin/bash

# Updates und Neustart
apt --yes -q update
apt --yes --force-yes -q upgrade
shutdown -r now
