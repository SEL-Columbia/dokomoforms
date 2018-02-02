#!/usr/bin/env bash

# In order to export the DISPLAY environment variable you should source this
# script rather than just executing it. Of course, you could export it
# yourself.

set -e
apt-get update
apt-get -y install xvfb iceweasel nodejs
pip install tox
Xvfb :1 -screen 0 1280x1280x16 &>/dev/null &
export DISPLAY=:1.0
printf "====================================================\n"
printf "If you didn't source this file, execute\n"
printf "export DISPLAY=:1.0\n\n"
printf "Now you can run any tox command. Don't use xvfb-run.\n"
printf "====================================================\n"
