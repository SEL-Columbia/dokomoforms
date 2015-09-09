"""TornadoResource class for dokomoforms.models.user.User."""
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
