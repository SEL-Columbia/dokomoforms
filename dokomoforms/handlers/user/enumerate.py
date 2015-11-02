"""Survey view handler."""
from restless.exceptions import Unauthorized

import tornado.web

from dokomoforms.handlers.util import BaseHandler, auth_redirect
from dokomoforms.handlers.api.v0 import get_survey_for_handler
from dokomoforms.options import options
from dokomoforms.models import Survey


class EnumerateHomepageHandler(BaseHandler):

    """The endpoint for the main Enumerator interface."""

    @tornado.web.authenticated
    def get(self):
        """GET the enumerate interface."""
        self.render('enumerate_homepage.html')


class Enumerate(BaseHandler):

    """View and submit to a survey."""

    def get(self, survey_id):
        """GET the main survey view.

        Render survey page for given survey id, embed JSON into to template so
        browser can cache survey in HTML.

        Raises tornado http error.

        @survey_id: Requested survey id.
        """
        try:
            survey = get_survey_for_handler(self, survey_id)
        except Unauthorized:
            return auth_redirect(self)

        # Raise a 403 if the logged-in user is not explicitly listed as an
        # enumerator. This might not be the behavior we want, since this
        # excludes the creator and any adminstrators who are not also
        # enumerators.
        # TODO: change the implementation (this does a naive check)
        # TODO: rethink user permission structure
        try:
            enumerators = survey.enumerators
        except AttributeError:
            pass
        else:
            if self.current_user_model not in enumerators:
                raise tornado.web.HTTPError(403)

        # pass in the revisit url
        self.render(
            'view_enumerate.html',
            survey=survey,
            revisit_url=options.revisit_url
        )


class EnumerateTitle(BaseHandler):

    """View and submit to a survey identified by title."""

    def get(self, title):
        """GET the main survey view.

        Render survey page for given survey title, embed JSON into to template
        so browser can cache survey in HTML.

        Checks for Survey.url_slug

        Raises tornado http error.
        """
        survey_id = (
            self.session
            .query(Survey.id)
            .filter_by(url_slug=title)
            .scalar()
        )
        if survey_id is None:
            raise tornado.web.HTTPError(404)
        Enumerate.get(self, survey_id)
