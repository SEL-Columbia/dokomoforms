"""Allow access to the auth_user table."""
from sqlalchemy import Table, MetaData
from sqlalchemy.sql.dml import Insert
from sqlalchemy.engine import RowProxy

from db import engine


auth_user_table = Table('auth_user', MetaData(bind=engine), autoload=True)


def check_password_hash(hashed_pw: str, password: str) -> bool:
    """
    Verify that a password matches a known hash.

    :param hashed_pw: The hashed password from the database.
    :param password: The raw password taken from user input.
    :raise NotImplementedError: We should use a framework.
    """
    raise NotImplementedError(
        'This is easy to mess up. We should use a framework.')


def hash_password(raw_password: str) -> str:
    """
    Hash and salt the user's password.

    :param raw_password: what the user entered
    :raise NotImplementedError: we need to decide how to approach this
    """
    raise NotImplementedError('How do we want to hash the password?')


def get_auth_user(auth_user_id: str) -> RowProxy:
    """
    Get a record from the auth_user table identified by auth_user_id.

    :param auth_user_id: primary key
    :return: the record
    """
    select_stmt = auth_user_table.select()
    where_stmt = select_stmt.where(
        auth_user_table.c.auth_user_id == auth_user_id)
    return where_stmt.execute().first()


def check_login(*, email: str, raw_password: str) -> RowProxy:
    """
    Return the user's details specified by the email and password.

    :param email: the supplied e-mail address
    :param raw_password: the supplied password
    :return: the record from the auth_user table
    :raise IncorrectPasswordError: if the password's hash doesn't match
    """
    select_stmt = auth_user_table.select()
    where_stmt = select_stmt.where(auth_user_table.c.email == email)
    user = where_stmt.execute().first()
    if check_password_hash(user.password, raw_password):
        return user
    else:
        raise IncorrectPasswordError(email)


def create_auth_user(*, email: str, raw_password: str) -> Insert:
    """
    Create a user account in the database. The database will store the hash
    of the supplied password. Make sure to use a transaction!

    :param email: The user's e-mail address
    :param raw_password: The password supplied by the user. This will be
                         salted and hashed.
    :return: The Insert object. Execute this!
    """
    hashed_password = hash_password(raw_password)
    return auth_user_table.insert().values(email=email,
                                           password=hashed_password)


class IncorrectPasswordError(Exception):
    """The supplied password's hash doesn't match what's in the database."""
    pass
