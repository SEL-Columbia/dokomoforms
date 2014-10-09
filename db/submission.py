from db import engine
from sqlalchemy import Table, MetaData

submission_table = Table('submission', MetaData(bind=engine), autoload=True)


def submission_insert(**values):
    return submission_table.insert().values(values)
