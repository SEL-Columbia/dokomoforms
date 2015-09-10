"""TornadoResource class for dokomoforms.models.user.User."""
from sqlalchemy.orm.exc import NoResultFound

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

    def create(self):
        """Create a new user."""
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
        if 'emails' in self.data:
            self.data['emails'] = [
                self._email(address) for address in self.data['emails']
            ]
        self._modify_survey_data('allowed_surveys')
        self._modify_survey_data('admin_surveys')
        self._modify_survey_data('surveys')
        return super().update(user_id)
