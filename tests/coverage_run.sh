set -e
coverage erase
coverage run --source=dokomoforms,webapp.py --branch -m unittest "$@"
coverage html
coverage report -m
