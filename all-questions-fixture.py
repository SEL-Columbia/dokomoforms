#!/usr/bin/env python3

import datetime
from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker

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
        name='test_user',
        # known ID against which we can test
        id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
        emails=[models.Email(address='test_creator@fixtures.com')],
    )

    node_types = list(models.NODE_TYPES)
    survey = models.Survey(
        id='b0816b52-204f-41d4-aaf0-ac6ae2970923',
        title={'English':'test_survey'},
        nodes=[ models.construct_survey_node(
                    type_constraint=node_type,
                    title={'English': node_type + '_node'},
                ) for node_type in node_types ],
        )

    # Add survey to creator
    creator.surveys.append(survey)

    # Finally save the creator
    session.add(creator)
