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
    creator = models.Administrator(
        name='Stet Tarcoea',
        emails=[models.Email(address='stet@dokomodata.org')],
    )

    node_types = list(models.NODE_TYPES)
    education_survey = models.Survey(
        id='b0816b52-204f-41d4-aaf0-ac6ae2970923',
        title={'English': 'Education Facility Survey'},
        nodes=[
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='photo',
                    title={'English': 'Photo of Facility Exterior'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='location',
                    title={'English': 'Location (GPS Coordinates)'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='facility',
                    title={'English': 'Facility'},
                    hint={'English': 'Select the facility from the list,'
                          ' or add a new one.'},
                    # NYC
                    logic={
                        'slat': 40.477398,
                        'nlat': 40.91758,
                        'wlng': -74.259094,
                        'elng': -73.700165,
                    }
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='text',
                    title={'English': 'Community Name'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='text',
                    title={'English': 'Facility Name'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='multiple_choice',
                    title={'English': 'Education Type'},
                    choices=[
                        models.Choice(
                            choice_text={
                                'English': 'government',
                            }
                        ),
                        models.Choice(
                            choice_text={
                                'English': 'private',
                            }
                        )
                    ]
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='multiple_choice',
                    title={'English': 'Education Level'},
                    choices=[
                        models.Choice(
                            choice_text={
                                'English': 'primary',
                            }
                        ),
                        models.Choice(
                            choice_text={
                                'English': 'secondary',
                            }
                        ),
                        models.Choice(
                            choice_text={
                                'English': 'both',
                            }
                        )
                    ]
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Total Number of Students'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Number of Male Students'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Number of Female Students'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Total Number of Full-time Teachers'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Total Number of Classrooms'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Number of Classrooms Needing Repair'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Number of Classrooms with '
                                      'Useable Blackboard'}
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='multiple_choice',
                    title={'English': 'Type of Water Point within 100 '
                                      'Meters of Facility'},
                    allow_other=True,
                    choices=[
                        models.Choice(
                            choice_text={
                                'English': 'none',
                            },
                        ),
                        models.Choice(
                            choice_text={
                                'English': 'handpump',
                            },
                        ),
                        models.Choice(
                            choice_text={
                                'English': 'tap',
                            }
                        )
                    ]
                )
            ),
            models.construct_survey_node(
                node=models.construct_node(
                    type_constraint='integer',
                    title={'English': 'Number of Improved Toilets'}
                )
            )
        ],
    )

    # Add survey to creator
    creator.surveys.append(education_survey)

    # Finally save the creator
    session.add(creator)
