"""Functions for interacting with API tokens."""
from datetime import timedelta

from db import engine
from db.auth_user import get_auth_user_by_email, generate_api_token, \
    set_api_token


def generate_token(data: dict) -> dict:
    """
    Generates a new API token for a user specified by e-mail address. You
    can supply a duration in seconds.

    :param data: the user's e-mail and an optional duration
    :return: the generated token and the token's expiration time
    """
    user = get_auth_user_by_email(data['email'])
    token = generate_api_token()
    params = {'token': token,
              'auth_user_id': user.auth_user_id}
    if 'duration' in data:
        duration = float(data['duration'])
        if duration > 31536000:
            raise TokenDurationTooLong(data['duration'])
        params['expiration'] = timedelta(seconds=duration)

    with engine.begin() as connection:
        connection.execute(set_api_token(**params))
    updated_user = get_auth_user_by_email(data['email'])
    return {'token': token,
            'expires_on': updated_user.expires_on.isoformat()}


class TokenDurationTooLong(Exception):
    """An API token cannot be valid for longer than 365 days."""
    pass
