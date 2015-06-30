""" Survey view handler."""

import tornado.web

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.api import SurveyResource #, SubmissionResource
from dokomoforms.models import Survey
from dokomoforms.models import ModelJSONEncoder
import json


class Enumerate(BaseHandler):
    def get(self, survey_id):
        """
        Render survey page for given survey id, embed JSON into to template so 
        browser can cache survey in HTML.

        Raises tornado http error.

        @survey_id: Requested survey id.
        """

        # Retrieve model from session 
        survey_model = self.session.query(Survey).get(survey_id)

        if not survey_model:
            raise tornado.web.HTTPError(404)

        # Create survey resource instance to access api prepare methods
        sr = SurveyResource()
        survey = sr.prepare(survey_model);

        self.render('survey.html',
                    survey_title=survey['title'],
                    # JSONify same way API does
                    survey=json.dumps(survey, cls=ModelJSONEncoder)),
