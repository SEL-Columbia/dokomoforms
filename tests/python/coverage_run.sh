#!/usr/bin/env bash
set -e
coverage erase
coverage run --source=dokomoforms,webapp.py --branch -m unittest ${@-discover tests}
coverage html
coverage report -m
