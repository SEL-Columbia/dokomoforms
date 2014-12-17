"""Allow access to the auth_user table."""

from sqlalchemy import Table, MetaData
from datetime import datetime

from sqlalchemy.sql.dml import Insert, Update
from sqlalchemy.engine import RowProxy
import uuid

from db import engine, update_record

from passlib.hash import bcrypt_sha256


auth_user_table = Table('auth_user', MetaData(bind=engine), autoload=True)


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
    raise NotImplementedError()


def create_auth_user(*, email: str) -> Insert:
    """
    Create a user account in the database. Make sure to use a transaction!

    :param email: The user's e-mail address
    :return: The Insert object. Execute this!
    """
    return auth_user_table.insert().values(email=email)


def generate_api_token() -> str:
    """
    Uses UUID4 to generate an API token.

    :return: The token as an alphanumeric string.
    """
    return ''.join(ch for ch in str(uuid.uuid4()).printable if ch.isalnum())


def verify_api_token(*, token: str, auth_user_id: str) -> bool:
    """
    Checks whether the supplied API token is valid for the specified user.

    :param token: the API token
    :param auth_user_id: the id of the user
    :return: whether the token is correct and not expired
    """
    auth_user = get_auth_user(auth_user_id)
    token_is_fresh = auth_user.expires_on > datetime.now()
    token_matches = bcrypt_sha256.verify(token, auth_user.token)

    return token_is_fresh and token_matches


def set_api_token(*,
                  expiration='60 days',
                  token: str,
                  auth_user_id: str) -> Update:
    """
    Set a new API token for the given user.

    :param expiration: how long the token will be valid, 60 days by default.
    :param token:
    :param auth_user_id:
    :return: :rtype:
    """
    hashed_token = bcrypt_sha256.encrypt(token)
    return update_record(auth_user_table,
                         'auth_user_id',
                         auth_user_id,
                         token=hashed_token,
                         expires_on="now() + INTERVAL '{}'".format(expiration))


class UserDoesNotExistError(Exception):
    """The supplied e-mail address is not in the database."""
    pass


class IncorrectPasswordError(Exception):
    """The supplied password's hash doesn't match what's in the database."""
    pass
