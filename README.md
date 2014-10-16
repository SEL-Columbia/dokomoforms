<a href="https://magnum.travis-ci.com/SEL-Columbia/dokomoforms"><img src="https://magnum.travis-ci.com/SEL-Columbia/dokomoforms.svg?token=YQoxqgi37o2BmSPVXoMS&branch=master" border="0" /></a>

# About

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.
 
# Installation

## How to run the thing
1. Install PostgreSQL, the contributed packages, PostGIS, and the PostgreSQL server development packages:

   ```sh
   sudo apt-get install postgresql postgresql-contrib postgis postgresql-server-dev-all
   ```
   
   (or whatever the command is on your distribution)
   
2. `$ pip-python3 install -r requirements.txt` (or whatever the command is on your distribution)
3. Create a "doko" database (or whatever other name you want) and a system user (if desired -- the postgres default user should work fine) with access to that database.
4. Edit the [settings.py](settings.py) file with the correct PostgreSQL connection string.
5. `$ python3 manage_db.py --create`
6. `$ python3 webapp.py`
