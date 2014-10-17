"""Allow access to the answer_choice table."""
from sqlalchemy import Table, MetaData, select, exists
from sqlalchemy.sql import Insert

from db import engine


logical_constraint_table = Table('logical_constraint', MetaData(bind=engine),
                                 autoload=True)


def logical_constraint_exists(logical_constraint_name: str) -> bool:
    """
    Check whether the given logical constraint name exists in the
    logical_constraint table.

    :param logical_constraint_name: the constraint name
    :return: whether it exists in the table
    """
    table_column = logical_constraint_table.c.logical_constraint_name
    exist_stmt = exists().where(table_column == logical_constraint_name)

    # select expects a list or something... don't ask me
    select_argument = (exist_stmt,)
    # and engine.execute returns something crazy
    (does_exist, ), = engine.execute(select(select_argument))
    return does_exist


def insert_logical_constraint_name(logical_constraint_name: str) -> Insert:
    """
    Create a new record in the logical_constraint table.

    :param logical_constraint_name: The constraint name.
    """
    lc = logical_constraint_name
    return logical_constraint_table.insert().values(logical_constraint_name=lc)


class LogicalConstraintDoesNotExist(Exception):
    pass
