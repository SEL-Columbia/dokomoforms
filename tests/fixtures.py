from collections import OrderedDict
import json
import datetime
from decimal import Decimal

import psycopg2

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError

from psycopg2.extras import NumericRange, DateRange, DateTimeTZRange

import dokomoforms.models as models
import dokomoforms.models.survey
import dokomoforms.exc as exc
from dokomoforms.models.survey import Bucket

from dokomoforms.options import inject_options

inject_options(schema='doko_test')

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker

engine = models.create_engine(echo=False)
Session = sessionmaker()

connection = engine.connect()
transaction = connection.begin()
session = Session(bind=connection, autocommit=True)


creator = models.SurveyCreator(
    name='creator',
    emails=[models.Email(address='email')],
)
node_types = list(models.NODE_TYPES)
for node_type in node_types:
    survey = models.Survey(
        title=node_type + '_survey',
        nodes=[
            models.SurveyNode(
                node=models.construct_node(
                    type_constraint=node_type,
                    title=node_type + '_node',
                ),
            ),
        ],
    )
    creator.surveys.append(survey)
    session.add(creator)
