#!/usr/bin/env bash
# For the last line to work (exporting the DISPLAY environment variable)
# you should source this file rather than just executing it. Of course, you
# could export it yourself.
set -e
apt-get update
apt-get -y install xvfb iceweasel npm nodejs-legacy
pip install tox
Xvfb :1 -screen 0 1024x768x16 &>/dev/null  &
export DISPLAY=:1.0
