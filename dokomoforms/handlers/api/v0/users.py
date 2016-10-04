"""TornadoResource class for dokomoforms.models.user.User."""
from restless.exceptions import Unauthorized

from sqlalchemy.orm.exc import NoResultFound

from dokomoforms.handlers.api.v0 import BaseResource
from dokomoforms.exc import UserRequiresEmailError
from dokomoforms.models import User, Email, Survey, construct_user, get_model


class UserResource(BaseResource):

    """Restless resource for Users."""

    resource_type = User
    default_sort_column_name = 'name'
    objects_key = 'users'

    def _survey(self, survey_id: str) -> Survey:
        return get_model(self.session, Survey, survey_id)

    def _email(self, address: str) -> Email:
        """Get or create an Email."""
        try:
            return self.session.query(Email).filter_by(address=address).one()
        except NoResultFound:
            return Email(address=address)

    def _modify_survey_data(self, field_name: str):
        """The API asks for survey id, but the model wants Survey objects."""
        if field_name in self.data:
            self.data[field_name] = [
                self._survey(s_id) for s_id in self.data[field_name]
            ]

    def is_authenticated(self):
        """Return whether the user has authenticated."""
        return super().is_authenticated(admin_only=False)

    def detail(self, user_id):
        """Return a user's details."""
        is_admin = self.current_user_model.role == 'administrator'
        if not is_admin and self.current_user_model.id != user_id:
            raise Unauthorized()
        return super().detail(user_id)

    def create(self):
        """Create a new user."""
        if self.current_user_model.role != 'administrator':
            raise Unauthorized()
        if not self.data.get('emails'):
            raise UserRequiresEmailError()
        self.data['emails'] = [
            Email(address=address) for address in self.data['emails']
        ]
        self._modify_survey_data('allowed_surveys')
        self._modify_survey_data('admin_surveys')
        with self.session.begin():
            user = construct_user(**self.data)
            self.session.add(user)
        return user

    def update(self, user_id):
        """Update a user."""
        is_admin = self.current_user_model.role == 'administrator'
        if not is_admin and self.current_user_model.id != user_id:
            raise Unauthorized()
        if 'emails' in self.data:
            self.data['emails'] = [
                self._email(address) for address in self.data['emails']
            ]
        self._modify_survey_data('allowed_surveys')
        self._modify_survey_data('admin_surveys')
        self._modify_survey_data('surveys')
        return super().update(user_id)

    def list(self):
        """Return the details for a list of users."""
        if self.current_user_model.role != 'administrator':
            raise Unauthorized()
        return super().list()

    def delete(self, user_id):
        """Delete a user."""
        if self.current_user_model.role != 'administrator':
            raise Unauthorized()
        super().delete(user_id)
