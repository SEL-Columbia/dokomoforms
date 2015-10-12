#!/usr/bin/env python3
"""Create fixtures for test purposes."""
import datetime

from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    import sys
    import os
    sys.path.insert(0, os.path.abspath('.'))
    from dokomoforms.options import parse_options
    parse_options()

import dokomoforms.models as models


Session = sessionmaker()


def load_fixtures(engine):
    """Create test users, surveys, and submissions."""
    # creates db schema
    session = Session(bind=engine, autocommit=True)

    with session.begin():
        creator = models.Administrator(
            name='test_user',
            # known ID against which we can test
            id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
            emails=[models.Email(address='test_creator@fixtures.com')],
        )
        creator_b = models.Administrator(
            name='test_user_b',
            # known ID against which we can test
            id='e7becd02-1a3f-4c1d-a0e1-286ba121aef1',
            emails=[models.Email(address='test_creator_b@fixtures.com')],
        )
        enumerator = models.User(
            name='test_user',
            # known ID against which we can test
            id='a7becd02-1a3f-4c1d-a0e1-286ba121aef3',
            emails=[models.Email(address='test_enumerator@fixtures.com')],
        )
        node_types = list(models.NODE_TYPES)
        for node_type in node_types:
            node_dict = {
                'title': {'English': node_type + '_node'},
                'type_constraint': node_type,
            }
            if node_type == 'facility':
                node_dict['logic'] = {
                    'slat': 39,
                    'nlat': 41,
                    'wlng': -71,
                    'elng': -69,
                }
            survey = models.Survey(
                title={'English': node_type + '_survey'},
                nodes=[
                    models.construct_survey_node(
                        node=models.construct_node(**node_dict),
                    ),
                ],
            )
            creator.surveys.append(survey)

            # Add a single submission per survey
            regular_submission = models.PublicSubmission(
                survey=survey,
                submitter_name='regular'
            )
            session.add(regular_submission)

        # Add another survey with known ID
        single_survey = models.Survey(
            id='b0816b52-204f-41d4-aaf0-ac6ae2970923',
            title={'English': 'single_survey'},
            nodes=[
                models.construct_survey_node(
                    id="60e56824-910c-47aa-b5c0-71493277b43f",
                    node=models.construct_node(
                        id="60e56824-910c-47aa-b5c0-71493277b43f",
                        title={'English': 'integer node'},
                        type_constraint='integer',
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
                                        title={'English': 'decimal node'},
                                        type_constraint='decimal',
                                    ),
                                    sub_surveys=[
                                        models.SubSurvey(
                                            buckets=[
                                                models.construct_bucket(
                                                    bucket_type='decimal',
                                                    bucket='(1.3, 2.3]'
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                                models.construct_survey_node(
                                    node=models.construct_node(
                                        title={'English': 'integer node'},
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
                                        )
                                    ],
                                ),
                                models.construct_survey_node(
                                    node=models.construct_node(
                                        title={'English': 'date node'},
                                        type_constraint='date',
                                    ),
                                    sub_surveys=[
                                        models.SubSurvey(
                                            buckets=[
                                                models.construct_bucket(
                                                    bucket_type='date',
                                                    bucket=(
                                                        '(2015-1-1, 2015-2-2]'
                                                    )
                                                ),
                                            ],
                                        ),
                                    ],
                                )
                            ]
                        ),
                    ],
                ),
                models.construct_survey_node(
                    id="80e56824-910c-47aa-b5c0-71493277b439",
                    allow_dont_know=True,
                    node=models.construct_node(
                        id="80e56824-910c-47aa-b5c0-71493277b439",
                        title={'English': 'Mutliple Choices'},
                        type_constraint='multiple_choice',
                        allow_other=True,
                        choices=[
                            models.Choice(
                                id="99956824-910c-47aa-b5c0-71493277b439",
                                choice_text={"English": "first choice"}),
                            models.Choice(
                                id="11156824-910c-47aa-b5c0-71493277b439",
                                choice_text={"English": "second choice"}),
                        ]
                    )
                ),
            ],
        )

        # Add another survey with known ID for creator_b
        single_survey_c_b = models.Survey(
            id='d0816b52-204f-41d4-aaf0-ac6ae2970923',
            title={'English': 'single_survey_c_b'},
            nodes=[],
        )

        # Add an enumerator only survey with known ID
        single_enum_survey = models.EnumeratorOnlySurvey(
            id='c0816b52-204f-41d4-aaf0-ac6ae2970925',
            title={'English': 'enumerator_only_single_survey'},
            nodes=[
                models.construct_survey_node(
                    allow_dont_know=True,
                    node=models.construct_node(
                        title={'English': 'Engine Room Photo'},
                        hint={'English': (
                            'Tap the image to capture a photo. Tap a '
                            'thumbnail to preview/delete captured photos.'
                        )},
                        type_constraint='photo',
                        allow_multiple=True
                    )
                ),
            ],
            enumerators=[
                creator
            ]
        )

        # Add another public submission with a known ID
        single_regular_submission = models.PublicSubmission(
            id='b0816b52-204f-41d4-aaf0-ac6ae2970924',
            survey=single_survey,
            submitter_name='regular_singular',
            answers=[
                models.construct_answer(
                    survey_node=single_survey.nodes[0],
                    type_constraint='integer',
                    answer=3,
                ),
            ]
        )
        session.add(single_regular_submission)

        # Add 100 public submissions over the past 100 days
        today = datetime.date.today()
        for i in range(0, 100):
            sub_time = today - datetime.timedelta(days=i)
            sub = models.PublicSubmission(
                survey=single_survey,
                submitter_name='regular',
                save_time=sub_time,
                submission_time=sub_time,
            )
            session.add(sub)

        # Add surveys to creator and enumerator
        creator.surveys.append(single_survey)
        creator_b.surveys.append(single_survey_c_b)
        creator.surveys.append(single_enum_survey)
        enumerator.allowed_surveys.append(single_enum_survey)

        # Finally save the creator and enumerator
        session.add(creator)
        session.add(creator_b)
        session.add(enumerator)


def unload_fixtures(engine, schema_name):
    """Truncate all the tables."""
    connection = engine.connect()
    with connection.begin():
        connection.execute(
            """
            DO
            $func$
            BEGIN
              EXECUTE (
                SELECT 'TRUNCATE TABLE '
                  || string_agg(
                       '{0}.' || quote_ident(t.tablename), ', '
                     )
                  || ' CASCADE'
                FROM   pg_tables t
                WHERE  t.schemaname = '{0}'
              );
            END
            $func$;
            """.format(schema_name)
        )


if __name__ == '__main__':
    from sqlalchemy import DDL
    from dokomoforms.options import options
    from dokomoforms.models import create_engine, Base
    engine = create_engine(echo=options.debug)
    engine.execute(DDL(
        'DROP SCHEMA IF EXISTS {} CASCADE'.format(options.schema))
    )
    Base.metadata.create_all(engine)
    load_fixtures(engine)
