<a href="https://magnum.travis-ci.com/SEL-Columbia/dokomoforms"><img src="https://magnum.travis-ci.com/SEL-Columbia/dokomoforms.svg?token=YQoxqgi37o2BmSPVXoMS&branch=master" border="0" /></a>

# About

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.
 
# Installation

1. Install PostgreSQL, the contributed packages, PostGIS, and the PostgreSQL server development packages:

   ```sh
   sudo apt-get install postgresql postgresql-contrib postgis postgresql-server-dev-all
   ```
   
   (or whatever the command is on your distribution)
   
   [Debian](http://www.debian.org/) users: update your apt sources according to [this guide](https://wiki.postgresql.org/wiki/Apt) else you will pull your hair out wondering why <tt>CREATE EXTENSION "postgis";</tt> fails.
   
2. `$ pip-python3 install -r requirements.txt` (or whatever the command is on your distribution)
3. Create a "doko" database (or whatever other name you want) and a system user (if desired -- the postgres default user should work fine) with access to that database.
4. Edit the [settings.py](settings.py) file with the correct PostgreSQL connection string.

   If you run <tt>manage_db.py</tt> as user <tt>postgres</tt> (and because of the extension creation commands, you basically have to), here is how to change the <tt>postgres</tt> *database* (as opposed to unix user) password:
   
   ```sh
   # sudo su - postgres
   $ psql
psql (9.3.5)
Type "help" for help.

postgres=# \password postgres
Enter new password: 
Enter it again: 
postgres=# \q
   ```
   
   Now, run the next command (number 5) as unix user <tt>postgres</tt>.
   
5. `$ python3 manage_db.py --create`
6. `$ python3 webapp.py`

# Running the tests

1. `$ pip-python3 install nose coverage`
2. `$ nosetests --with-coverage --cover-inclusive --cover-branches --cover-html --cover-erase --cover-package=api,db,webapp`

