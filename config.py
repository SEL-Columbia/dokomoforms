"""
Treat this as a read-only file! It sets the defaults for the configuration
values.

If you want to use different values, set them as command line arguments:
    $ python3 webappy.py --port=8889
or place them in a file called local_config.py (which is in the .gitignore
file).
"""

port = 8888
db_host = 'localhost:5432'
db_database = 'doko'
db_user = 'postgres'
db_password = 'whatever your password is'

cookie_secret = 'big secret'

try:
    from local_config import *
except ImportError:
    pass
