"""Functions for interacting with user accounts."""
from db import engine
from db.auth_user import get_auth_user_by_email, create_auth_user


def create_user(data: dict) -> dict:
    """
    Registers a new user account.

    :param data: the user's e-mail
    :return: a response containing the e-mail and whether it was created or
    already exists in the database
    """
    email = data['email']
    if get_auth_user_by_email(email) is None:
        with engine.begin() as connection:
            connection.execute(create_auth_user(email=email))
        return {'email': email, 'response': 'Created'}
    else:
        return {'email': email, 'response': 'Already exists'}
