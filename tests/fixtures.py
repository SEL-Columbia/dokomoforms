import datetime
from sqlalchemy import DDL
from sqlalchemy.orm import sessionmaker

import dokomoforms.models as models


Session = sessionmaker()


def load_fixtures(engine):
    # creates db schema
    session = Session(bind=engine, autocommit=True)

    with session.begin():
        creator = models.SurveyCreator(
            name='test_user',
            # known ID against which we can test
            id='b7becd02-1a3f-4c1d-a0e1-286ba121aef4',
            emails=[models.Email(address='test_creator@fixtures.com')],
        )
        creator_b = models.SurveyCreator(
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
            survey = models.Survey(
                title={'English': node_type + '_survey'},
                nodes=[
                    models.construct_survey_node(
                        node = models.construct_node(
                            title={'English': node_type + '_node'},
                            type_constraint=node_type,
                        ),
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
                    # NOTE: this becomes the ID for both the SurveyNode
                    # and the Node.
                    id="60e56824-910c-47aa-b5c0-71493277b43f",
                    node = models.construct_node(
                        title={'English': 'integer node'},
                        type_constraint='integer',
                    ),
                )
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
            nodes=[],
        )

        # Add another public submission with a known ID
        single_regular_submission = models.PublicSubmission(
            id='b0816b52-204f-41d4-aaf0-ac6ae2970923',
            survey=single_survey,
            submitter_name='regular',
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
                submission_time=sub_time
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

    # while True:
    #    pass


def unload_fixtures(engine, schema_name):
    print('unload_fixtures')
    engine.execute(DDL('DROP SCHEMA IF EXISTS ' + schema_name + ' CASCADE'))
