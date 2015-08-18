#!/usr/bin/env python3
"""Strange fixture."""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from dokomoforms.options import parse_options, options
parse_options()

from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker

from dokomoforms.models import create_engine, Base
import dokomoforms.models as models

engine = create_engine(echo=options.debug)
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
                    type_constraint='integer',
                    title={'English': 'integer' + ' node'},
                    hint={
                        'English': (
                            'fill in response for ' + 'integer' + ' node'
                        )
                    },
                    allow_multiple=False,
                ),
                sub_surveys=[
                    models.SubSurvey(
                        buckets=[
                            models.construct_bucket(
                                bucket_type='integer',
                                bucket='(, 2]'
                            ),
                        ],

                        nodes=[
                            models.construct_survey_node(
                                node=models.construct_node(
                                    title={
                                        'English': 'date sub node (nested)'
                                    },
                                    type_constraint='date',
                                ),
                                sub_surveys=[
                                    models.SubSurvey(
                                        buckets=[
                                            models.construct_bucket(
                                                bucket_type='date',
                                                bucket=(
                                                    '(2011-01-01, 2014-01-02]'
                                                )
                                            ),
                                        ],

                                        nodes=[
                                            models.construct_survey_node(
                                                required=True,
                                                node=models.construct_node(
                                                    title={
                                                        'English': (
                                                            'integer sub'
                                                            ' suuubb node'
                                                            ' (required)'
                                                        )
                                                    },
                                                    type_constraint='integer',
                                                ),
                                            ),

                                            models.construct_survey_node(
                                                node=models.construct_node(
                                                    title={
                                                        'English': (
                                                            'date sub suuubb '
                                                            'node'
                                                        )
                                                    },
                                                    type_constraint='date',
                                                ),

                                            ),
                                            models.construct_survey_node(
                                                node=models.construct_node(
                                                    title={
                                                        'English': (
                                                            'text sub suuubb'
                                                            ' node'
                                                        )
                                                    },
                                                    type_constraint='text',
                                                ),
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                    ),

                    models.SubSurvey(
                        buckets=[
                            models.construct_bucket(
                                bucket_type='integer',
                                bucket='(2, 5]'
                            ),
                        ],
                        nodes=[
                            models.construct_survey_node(
                                node=models.construct_node(
                                    title={'English': 'text sub 1'},
                                    type_constraint='text',
                                ),
                            ),
                            models.construct_survey_node(
                                node=models.construct_node(
                                    title={'English': 'text sub 2'},
                                    type_constraint='text',
                                ),
                            ),

                            models.construct_survey_node(
                                node=models.construct_node(
                                    title={'English': 'text sub 3'},
                                    type_constraint='text',
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    node = models.construct_node(
        type_constraint='multiple_choice',
        title={'English': 'multiple choice' + ' node'},
        hint={'English': 'choose your weapon'},
        allow_other=True,
        choices=[
            models.Choice(
                choice_text={
                    'English': 'choice ' + str(i),
                },
            ) for i in range(3)
        ],
    )

    survey.nodes.append(models.construct_survey_node(
        allow_dont_know=True,
        required=False,
        node=node,
        sub_surveys=[
            models.SubSurvey(
                buckets=[
                    models.construct_bucket(
                        bucket_type='multiple_choice',
                        bucket=node.choices[1],
                        ),
                    ],

                nodes=[
                    models.construct_survey_node(
                        node=models.construct_node(
                            title={'English': 'mc text sub 1'},
                            type_constraint='text',
                            ),
                        ),
                    models.construct_survey_node(
                        node=models.construct_node(
                            title={'English': 'mc text sub 2'},
                            type_constraint='text',
                            ),
                        ),
                    ]
                )
            ]
    ))

    survey.nodes.append(models.construct_survey_node(
        node=models.construct_node(
            type_constraint='note',
            title={'English': 'End note' + ' node'},
        ),
    ))

    # Add survey to creator
    creator.surveys.append(survey)

    # Finally save the creator
    session.add(creator)
