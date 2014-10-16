"""Allow access to the answer_choice table."""
from sqlalchemy import Table, MetaData, select, exists

from db import engine


logical_constraint_table = Table('logical_constraint', MetaData(bind=engine),
                                 autoload=True)


def insert_logical_constraint_if_necessary(logical_constraint_name):
    """
    Create a new record in the logical_constraint table if the supplied name
    does not exist already.

    :param logical_constraint_name: The constraint name.
    """
    lcn = logical_constraint_name
    table_column = logical_constraint_table.c.logical_constraint_name
    exist_stmt = exists().where(table_column == lcn)
    # engine.execute expects a list or something... don't ask me
    (does_exist, ) = engine.execute((select(exist_stmt),))
    if not does_exist:
        logical_constraint_table.insert().values(logical_constraint_name=lcn)
