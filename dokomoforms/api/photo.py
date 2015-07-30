"""TornadoResource class for dokomoforms.models.answer.Photo."""
from dokomoforms.api import BaseResource
from dokomoforms.models import Photo, add_new_photo_to_session


class PhotoResource(BaseResource):

    """Restless resource for Photos."""

    resource_type = Photo
    default_sort_column_name = 'created_on'
    objects_key = 'photos'

    def is_authenticated(self):
        """Allow unauthenticated POSTs."""
        if self.request_method() == 'POST':
            return True
        return super().is_authenticated()

    def create(self):
        """Create a Photo. Must match an existing PhotoAnswer."""
        authenticated = super().is_authenticated()
        if not authenticated:
            self._check_xsrf_cookie()

        return add_new_photo_to_session(self.session, **self.data)
