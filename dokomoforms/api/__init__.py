"""The dokomo JSON API"""
from collections import Iterator

from sqlalchemy.engine import ResultProxy, Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Insert, Update


def execute_with_exceptions(connection: Connection,
                            executable: [Insert, Update],
                            exceptions: Iterator) -> ResultProxy:
    """
    Execute the given executable (a SQLAlchemy Insert or Update) within a
    transaction (provided by the Connection object), and raise meaningful
    exceptions. Normally connection.execute() will raise a generic Integrity
    error, so use the exceptions parameter to specify which exceptions to
    raise instead.

    :param connection: the SQLAlchemy connection (for transaction purposes)
    :param executable: the object to pass to connection.execute()
    :param exceptions: an iterable of (name: str, exception: Exception) tuples.
                       name is the string to look for in the IntegrityError,
                       and exception is the Exception to raise instead of
                       IntegrityError
    :return: a SQLAlchemy ResultProxy
    """
    try:
        return connection.execute(executable)
    except IntegrityError as exc:
        error = str(exc.orig)
        for name, exception in exceptions:
            if name in error:
                raise exception
        raise


def json_response(something: object) -> dict:
    """
    Turns out a list isn't real JSON.

    :param something: anything, especially a list
    :return: {'result': something}
    """
    return {'result': something}


def maybe_isoformat(date_or_time) -> str:
    """
    Return the date_or_time.isoformat() if date_or_time is not None,
    else the empty string.

    :param date_or_time: a Python date, time, etc.
    :return: the ISO 8601 representation (or the empty string)
    """
    return '' if date_or_time is None else date_or_time.isoformat()
