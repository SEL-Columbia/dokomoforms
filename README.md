# About
[![Build Status](https://travis-ci.org/SEL-Columbia/dokomoforms.svg?branch=master)](https://travis-ci.org/SEL-Columbia/dokomoforms)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/SEL-Columbia/dokomoforms?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Coverage Status](https://coveralls.io/repos/SEL-Columbia/dokomoforms/badge.svg?branch=master)](https://coveralls.io/r/SEL-Columbia/dokomoforms?branch=master)

[![Sauce Test Status](https://saucelabs.com/browser-matrix/dokomo_sauce_matrix.svg)](https://saucelabs.com/u/dokomo_sauce_matrix)

[![Dependency Status](https://gemnasium.com/SEL-Columbia/dokomoforms.svg)](https://gemnasium.com/SEL-Columbia/dokomoforms)

[![Documentation Status](https://readthedocs.org/projects/dokomoforms/badge/?version=latest)](https://readthedocs.org/projects/dokomoforms/?badge=latest)

Dokomo [どこも](http://tangorin.com/general/%E3%81%A9%E3%81%93%E3%82%82) Forms is a mobile data collection technology that doesn't suck.

# Installation

1. Install PostgreSQL, the contributed packages, PostGIS, and the PostgreSQL server development packages:

   ```sh
   sudo apt-get install postgresql postgresql-contrib postgis postgresql-server-dev-all
   ```
   
   (or whatever the command is on your distribution)

   You may also need to install a package like postgresql-X.Y-postgis-scripts (check your repositories).
   
   [Debian](http://www.debian.org/) users: update your apt sources according to [this guide](https://wiki.postgresql.org/wiki/Apt) else you will pull your hair out wondering why <tt>CREATE EXTENSION "postgis";</tt> fails.
   
2. `$ pip-python3 install -r requirements.txt` (or whatever the command is on your distribution)
3. Create a "doko" database (or whatever other name you want) and a system user (if desired -- the postgres default user should work fine) with access to that database.
4. Edit your dokomoforms/local_settings.py file with the correct PostgreSQL `CONNECTION_STRING` (see [dokomoforms/settings.py](dokomoforms/settings.py)).

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

**Note that if `debug` is `True` in the `webapp.py` `config` variable, Anyone can log in as any user. DO NOT SET `debug` TO `True` IN PRODUCTION. Likewise, `APP_DEBUG=true` in local_settings.py sets the `debug` flag to `True`.** 

**Finally `TEST_USER=USER` in local_settings permanently logs user USER in for everyone, DO NOT SET THIS IN PRODUCTION.**

# Running the tests

1. `$ pip-python3 install nose coverage selenium`
2. `$ nosetests -c tox.ini`
  * **Note:** Selenium tests involve browser windows popping up. If this causes issues on your machine or you'd just prefer for that not to happen, install [Xvfb](http://en.wikipedia.org/wiki/Xvfb) and use this command instead: `xvfb-run nosetests -c tox.ini`

## Running Selenium tests on Sauce Labs

In order to make it easier to test across devices and browsers, you can run the Selenium tests on Sauce Labs.

1. Sign up for an account at [saucelabs.com](https://saucelabs.com/)
2. Install and run sauce-connect: https://docs.saucelabs.com/reference/sauce-connect/
3. Using your username and access key from Sauce Labs, edit your dokomoforms/local_settings.py file like so:

  ```
  SAUCE_CONNECT = True
  SAUCE_USERNAME = 'username'
  SAUCE_ACCESS_KEY = 'access key'
  DEFAULT_BROWSER = 'firefox::Linux'
  ```
