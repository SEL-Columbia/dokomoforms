"""Functions for interacting with user accounts."""
from datetime import timedelta

from sqlalchemy.engine import Connection

from api import json_response
from db.auth_user import get_auth_user_by_email, create_auth_user, \
    generate_api_token, set_api_token, UserDoesNotExistError


def create_user(connection: Connection, data: dict) -> dict:
    """
    Registers a new user account.

    :param connection: a SQLAlchemy Connection
    :param data: the user's e-mail
    :return: a response containing the e-mail and whether it was created or
    already exists in the database
    """
    email = data['email']
    try:
        get_auth_user_by_email(connection, email)
    except UserDoesNotExistError:
        with connection.begin():
            connection.execute(create_auth_user(email=email))
        return json_response({'email': email, 'response': 'Created'})
    return json_response({'email': email, 'response': 'Already exists'})


def generate_token(connection: Connection, data: dict) -> dict:
    """
    Generates a new API token for a user specified by e-mail address. You
    can supply a duration in seconds.

    :param connection: a SQLAlchemy Connection
    :param data: the user's e-mail and an optional duration
    :return: the generated token and the token's expiration time
    """
    user = get_auth_user_by_email(connection, data['email'])
    token = generate_api_token()
    params = {'token': token,
              'auth_user_id': user.auth_user_id}
    if 'duration' in data:
        duration = float(data['duration'])
        if duration > 31536000:
            raise TokenDurationTooLong(data['duration'])
        params['expiration'] = timedelta(seconds=duration)

    with connection.begin():
        connection.execute(set_api_token(**params))
    updated_user = get_auth_user_by_email(connection, data['email'])
    return json_response(
        {'token': token, 'expires_on': updated_user.expires_on.isoformat()})


class TokenDurationTooLong(Exception):
    """An API token cannot be valid for longer than 365 days."""
    pass
