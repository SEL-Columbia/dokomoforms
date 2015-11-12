"""Pages pertaining to demo mode functionality."""
import datetime

from sqlalchemy.orm.exc import NoResultFound

import dokomoforms.models as models
from dokomoforms.models import Administrator, Email
from dokomoforms.handlers.util import BaseHandler


def _create_demo_user(session):
    with session.begin():
        user = Administrator(
            name='demo_user',
            emails=[Email(address='demo@dokomoforms.org')],
        )
        survey = models.construct_survey(
            title={'English': 'Demo Education Survey'},
            survey_type='public',
            url_slug='demo',
            nodes=[
                models.construct_survey_node(
                    node=models.construct_node(
                        type_constraint='photo',
                        title={'English': 'Photo of Facility Exterior'}
                    )
                ),
                models.construct_survey_node(
                    node=models.construct_node(
                        type_constraint='facility',
                        title={'English': 'Facility'},
                        hint={'English': (
                            'Select the facility from the list, or add'
                            ' a new one.'
                        )},
                        logic={
                            'slat': -85,
                            'nlat': 85,
                            'wlng': -180,
                            'elng': 180,
                        }
                    )
                ),
                models.construct_survey_node(
                    node=models.construct_node(
                        type_constraint='multiple_choice',
                        title={'English': 'Education Type'},
                        choices=[
                            models.Choice(
                                choice_text={
                                    'English': 'public',
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
                        allow_other=True,
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
                        title={'English': 'Number of Students'},
                        logic={'min': 0}
                    )
                ),
            ],
        )
        user.surveys.append(survey)
        session.add(user)
        session.flush()
        survey.submissions.extend([
            models.construct_submission(
                submission_type='public_submission',
                submitter_name='Demo Submitter 1',
                submission_time=(
                    datetime.datetime.now() - datetime.timedelta(days=1)
                ),
                save_time=(
                    datetime.datetime.now() - datetime.timedelta(days=1)
                ),
                answers=[
                    models.construct_answer(
                        survey_node=survey.nodes[1],
                        type_constraint='facility',
                        answer={
                            'facility_id': 1,
                            'lat': 40.8,
                            'lng': -73.9,
                            'facility_name': 'Demo Facility 1',
                            'facility_sector': 'Demo',
                        },
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[2],
                        type_constraint='multiple_choice',
                        answer=survey.nodes[2].node.choices[1].id,
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[3],
                        type_constraint='multiple_choice',
                        other='Technical',
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[4],
                        type_constraint='integer',
                        answer=200,
                    ),
                ],
            ),
            models.construct_submission(
                submission_type='public_submission',
                submitter_name='Demo Submitter 2',
                submission_time=(
                    datetime.datetime.now() - datetime.timedelta(days=4)
                ),
                save_time=(
                    datetime.datetime.now() - datetime.timedelta(days=4)
                ),
                answers=[
                    models.construct_answer(
                        survey_node=survey.nodes[1],
                        type_constraint='facility',
                        answer={
                            'facility_id': 2,
                            'lat': 42,
                            'lng': -74,
                            'facility_name': 'Demo Facility 2',
                            'facility_sector': 'Demo',
                        },
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[2],
                        type_constraint='multiple_choice',
                        answer=survey.nodes[2].node.choices[0].id,
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[3],
                        type_constraint='multiple_choice',
                        answer=survey.nodes[3].node.choices[0].id,
                    ),
                    models.construct_answer(
                        survey_node=survey.nodes[4],
                        type_constraint='integer',
                        answer=300,
                    ),
                ],
            ),
        ])
        session.add(survey)
    return user


class DemoUserCreationHandler(BaseHandler):

    """Use this page to log in as the demo user."""

    def get(self):
        """Create the demo account (if necessary) and log in."""
        try:
            user = (
                self.session
                .query(Administrator)
                .filter_by(name='demo_user')
                .one()
            )
        except NoResultFound:
            user = _create_demo_user(self.session)
        cookie_options = {
            'expires_days': None,
            'httponly': True,
        }
        self.set_secure_cookie('user', user.id, **cookie_options)
        self.redirect('/')


class DemoLogoutHandler(BaseHandler):

    """Log out by visiting this page."""

    def get(self):
        """Clear the 'user' cookie."""
        self.clear_cookie('user')
        self.redirect('/')
