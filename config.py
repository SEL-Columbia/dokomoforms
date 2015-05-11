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
