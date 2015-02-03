#/usr/bin/env/sh
set -e
echo "Testing node bs"
export PYTHON=python2.7
npm install --python=python2.7
npm test
