from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker

from tornado.escape import json_decode, json_encode

import json

from dokomoforms.models import create_engine, Base
from dokomoforms.options import options, inject_options
import dokomoforms.models as models

inject_options(schema='doko')

# parse_options()


engine = create_engine(echo=True)
Session = sessionmaker()


engine.execute(DDL('DROP SCHEMA IF EXISTS ' + options.schema + ' CASCADE'))

# creates db schema
Base.metadata.create_all(engine)

# connection = engine.connect()
# transaction = connection.begin()
# session = Session(bind=connection, autocommit=True)
session = Session(bind=engine, autocommit=True)


with session.begin():
    creator = models.SurveyCreator(
        name='creator',
        emails=[models.Email(address='email')],
    )
    node_types = list(models.NODE_TYPES)
    for node_type in node_types:
        sn = (
            models.NonAnswerableSurveyNode if node_type == 'note' else
            models.AnswerableSurveyNode
        )
        survey = models.Survey(
            title=node_type + '_survey',
            nodes=[
                sn(
                    node=models.construct_node(
                        type_constraint=node_type,
                        title=node_type + '_node',
                    ),
                ),
            ],
        )
        creator.surveys.append(survey)
    session.add(creator)

session.close()
