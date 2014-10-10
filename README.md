![](https://magnum.travis-ci.com/SEL-Columbia/dokomoforms.svg?token=YQoxqgi37o2BmSPVXoMS&branch=master)

# About

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.
 
# Installation

## How to run the thing
1. `$ pip-python3 install -r requirements.txt` (or whatever the command is on your distribution)
2. Install and start PostgreSQL.
3. Edit the [settings.py](settings.py) file with the correct PostgreSQL connection string.
4. `$ python3 manage_db.py --create`
5. `$ python3 webapp.py`
