""" Survey view handler."""
import urllib.parse as urlparse
from urllib.parse import urlencode

import tornado.web

from restless.exceptions import Unauthorized

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.api import SurveyResource #, SubmissionResource
from dokomoforms.models import Survey


class Enumerate(BaseHandler):
    def get(self, survey_id):
        """
        Render survey page for given survey id, embed JSON into to template so 
        browser can cache survey in HTML.

        Raises tornado http error.

        @survey_id: Requested survey id.
        """
        survey_resource = SurveyResource()
        survey_resource.ref_rh = self
        try:
            survey = survey_resource.detail(survey_id)
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

        self.render('enumerate.html', survey=survey)
