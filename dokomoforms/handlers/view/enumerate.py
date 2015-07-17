"""Survey view handler."""
import urllib.parse as urlparse
from urllib.parse import urlencode

from restless.exceptions import Unauthorized

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.api import get_survey_for_handler


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
            url = self.get_login_url()
            if '?' not in url:
                if urlparse.urlsplit(url).scheme:
                    next_url = self.request.full_url()
                else:
                    next_url = self.request.uri
                url += '?' + urlencode({'next': next_url})
            self.redirect(url)
            return

        self.render('view_enumerate.html', survey=survey)
