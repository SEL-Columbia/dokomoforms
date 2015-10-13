"""Pages pertaining to demo mode functionality."""
import uuid

import dokomoforms.models as models
from dokomoforms.models import Administrator, Email
from dokomoforms.handlers.util import BaseHandler


class DemoUserCreationHandler(BaseHandler):

    """Use this page to create a demo user."""

    def get(self):
        """Create a new demo account and log in."""
        new_id = uuid.uuid4()
        name = 'demo-{}'.format(new_id)
        email = '{}@dokomoforms.org'.format(name)
        with self.session.begin():
            user = Administrator(
                name=name,
                emails=[Email(address=email)],
                surveys=[models.construct_survey(
                    title={'English': 'Demo Education Survey'},
                    survey_type='public',
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
                )],
            )
            self.session.add(user)
        cookie_options = {
            'expires_days': None,
            'httponly': True,
        }
        self.set_secure_cookie('user', user.id, **cookie_options)
        self.redirect('/')


class DemoLogoutHandler(BaseHandler):

    """Delete your demo account by visiting this page."""

    def get(self):
        """Clear the 'user' cookie and delete the user."""
        self.clear_cookie('user')
        if self.current_user_model:
            with self.session.begin():
                self.session.delete(self.current_user_model)
        self.redirect('/')
