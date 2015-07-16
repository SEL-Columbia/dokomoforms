#!/usr/bin/env python3
"""Strange fixture."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker
from dokomoforms.options import options, inject_options, parse_options

inject_options(
    schema='doko',
    # fake logged in user with ID from fixture
    TEST_USER="""
        {
            "user_id": "b7becd02-1a3f-4c1d-a0e1-286ba121aef4",
            "user_name": "test_user"
        }
    """
)
# inject_options(schema='doko_test')
parse_options()

from dokomoforms.models import create_engine, Base
import dokomoforms.models as models

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
        title={'English': 'test_survey'},
        nodes=[
            models.construct_survey_node(
                allow_dont_know=True,
                node=models.construct_node(
                    type_constraint=node_type,
                    title={'English': node_type + ' node'},
                    title={'English': 'fill in response for ' + node_type + ' node'},
                    allow_multiple=bool(i % 2),
                ),
                sub_surveys=[
                    models.SubSurvey(
                        buckets=[
                            models.construct_bucket(
                                bucket_type='integer',
                                bucket='(1, 2]'
                            ),
                        ],
                        nodes=[
                            models.construct_survey_node(
                                node=models.construct_node(
                                    title={'English': 'integer sub node'},
                                    type_constraint='integer',
                                ),
                                sub_surveys=[
                                    models.SubSurvey(
                                        buckets=[
                                            models.construct_bucket(
                                                bucket_type='integer',
                                                bucket='(1, 2]'
                                            ),
                                        ]
                                    ),
                                ],
                            )
                        ],
                    ) for i in range(1) if node_type == 'integer'],

            ) for node_type in node_types
            if node_type != 'note' and node_type != 'multiple_choice'
        ],
    )

    survey.nodes.append(models.construct_survey_node(
        allow_dont_know=True,
        required=True,
        node=models.construct_node(
            type_constraint='multiple_choice',
            title={'English': 'multiple_choice' + ' node'},
            allow_other=True,
            choices=[
                models.Choice(
                    choice_text={
                        'English': 'choice ' + str(i),
                    },
                ) for i in range(3)
            ],
        ),
    ))

    survey.nodes.append(models.construct_survey_node(
        node=models.construct_node(
            type_constraint='note',
            title={'English': 'note' + ' node'},
        ),
    ))

    # Add survey to creator
    creator.surveys.append(survey)

    # Finally save the creator
    session.add(creator)
