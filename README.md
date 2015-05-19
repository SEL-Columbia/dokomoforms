# About

Dokomo Forms is a self-hosted data collection and analysis platform, and is the successor to [Formhub](https://formhub.org/).

[![Build Status](https://travis-ci.org/SEL-Columbia/dokomoforms.svg?branch=master)](https://travis-ci.org/SEL-Columbia/dokomoforms)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/SEL-Columbia/dokomoforms?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Coverage Status](https://coveralls.io/repos/SEL-Columbia/dokomoforms/badge.svg?branch=master)](https://coveralls.io/r/SEL-Columbia/dokomoforms?branch=master)

[![Sauce Test Status](https://saucelabs.com/browser-matrix/dokomo_sauce_matrix.svg)](https://saucelabs.com/u/dokomo_sauce_matrix)

[![Dependency Status](https://gemnasium.com/SEL-Columbia/dokomoforms.svg)](https://gemnasium.com/SEL-Columbia/dokomoforms)

[![Documentation Status](https://readthedocs.org/projects/dokomoforms/badge/?version=latest)](https://readthedocs.org/projects/dokomoforms/?badge=latest)

# Phoenix

1. Organization owns instance, and all users belong to the organization. (TODO)

2. Filesystem-level encryption. (TODO)

3. i18n

4. Focus on questions rather than surveys. (TODO)

5. You can specify configuration options in `local_config.py` or as command line flags to [webapp.py](webapp.py)

6. [webapp.py](webapp.py) now sets up the tables for you (no more `manage_db.py`). If you want `$ manage_db.py -d`, run

  `$ ./webapp.py --kill=True`

  You can also specify the schema you want like `$ ./webappy.py --schema=whatever`

7. New way to run tests (after `$ pip install tox`):

  `$ tox`

  Or, if you want the coverage report as well,

  `$ tox -e cover`

  The tests only touch the `doko_test` schema (which they create/destroy for you).
