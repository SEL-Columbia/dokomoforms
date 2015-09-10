"""TornadoResource class for dokomoforms.models.user.User."""
from sqlalchemy.sql import exists

from dokomoforms.handlers.api import BaseResource
from dokomoforms.exc import UserRequiresEmailError
from dokomoforms.models import User, Email, Survey, construct_user, get_model


class UserResource(BaseResource):

    """Restless resource for Users."""

    resource_type = User
    default_sort_column_name = 'name'
    objects_key = 'users'

    def _survey(self, survey_id: str) -> Survey:
        return get_model(self.session, Survey, survey_id)

    def create(self):
        """Create a new user."""
        with self.session.begin():
            if not self.data.get('emails'):
                raise UserRequiresEmailError()
            self.data['emails'] = [
                Email(address=address) for address in self.data['emails']
            ]
            if 'allowed_surveys' in self.data:
                self.data['allowed_surveys'] = [
                    self._survey(s_id) for s_id in self.data['allowed_surveys']
                ]
            if 'admin_surveys' in self.data:
                self.data['admin_surveys'] = [
                    self._survey(s_id) for s_id in self.data['admin_surveys']
                ]
            user = construct_user(**self.data)
            self.session.add(user)
        return user

    def update(self, user_id):
        """Update a user."""
        user = self._get_model(user_id)

        with self.session.begin():
            if 'emails' in self.data:
                self.data['emails'] = [
                    self._getEmail(address) for address in self.data['emails']
                ]
            if 'allowed_surveys' in self.data:
                self.data['allowed_surveys'] = [
                    self._survey(s_id) for s_id in self.data['allowed_surveys']
                ]
            if 'surveys' in self.data:
                self.data['surveys'] = [
                    self._survey(s_id) for s_id in self.data['surveys']
                ]

            for attribute, value in self.data.items():
                print('------------------- \n')
                print('setting: ' + attribute)
                print('------------------- \n')
                setattr(user, attribute, value)
        return user

    def _getEmail(self, email_address):
        """Get an existing or create an Email from email_address"""

        email = (
            self.session.query(Email).filter(
                Email.address == email_address).one()
        )

        if email is not None:
            return email
        else:
            return Email(address=email_address)
