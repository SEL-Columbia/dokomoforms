"""Set up database access."""
from sqlalchemy import create_engine, Table
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Update, Delete

from settings import CONNECTION_STRING


engine = create_engine(CONNECTION_STRING, convert_unicode=True)


def set_testing_engine(testing_engine: Engine):
    """
    Use this function to set an alternate testing engine (like SQLite):

    import db

    from sqlalchemy import create_engine

    db.set_engine(create_engine(CONNECTION_STRING, convert_unicode=True))

    :param testing_engine: A SQLAlchemy engine
    """
    global engine
    engine = testing_engine


_UPD_TYPE_ERR = '''Cannot specify the update values in both a dict and
keyword arguments.'''


def update_record(table: Table,
                  uuid_column_name: str,
                  uuid_value: str,
                  values_dict: dict=None,
                  **values) -> Update:
    """
    Update a record in the specified table identified by the given primary
    key name and value. You can give the values to update in either the
    values_dict parameter or as keyword arguments.

    Make sure you use a transaction!

    >>> update_record(survey_table, 'survey_id', survey_id, title='new_title')
    <sqlalchemy.sql.dml.Update object at 0x...>

    >>> update_record(survey_table, 'survey_id', survey_id,
    {'title':'new_title'})
    <sqlalchemy.sql.dml.Update object at 0x...>


    :param table: The SQLAlchemy table
    :param uuid_column_name: The UUID primary key column name
    :param uuid_value: The UUID specifying the record
    :param values_dict: The new values. If given, you cannot also give
                        keyword arguments.
    :param values: The new values. If given, you cannot also give the
                   values_dict parameter.
    :return: A SQLAlchemy Update object. Execute this!
    """

    # Check that this function was called with either the value_dict
    # parameter or kwargs
    if values_dict:
        if values:
            raise TypeError(_UPD_TYPE_ERR)
        values = values_dict
    elif not values:
        raise TypeError('No update values specified.')
    # An update bumps the record's last_update_time column
    values[table.name + '_last_update_time'] = 'now()'
    condition = table.c.get(uuid_column_name) == uuid_value
    return table.update().where(condition).values(values)


def delete_record(table: Table,
                  uuid_column_name: str,
                  uuid_value: str) -> Delete:
    """
    Delete a record in the specified table identified by the given primary
    key name and value.

    >>> delete_record(survey_table, 'survey_id', survey_id)
    <sqlalchemy.sql.dml.Delete object at 0x...>

    Make sure you use a transaction!

    :param table: The SQLAlchemy table
    :param uuid_column_name: The UUID primary key column name
    :param uuid_value: The UUID specifying the record
    :return: A SQLAlchemy Delete object. Execute this!
    """
    return table.delete().where(table.c.get(uuid_column_name) == uuid_value)
