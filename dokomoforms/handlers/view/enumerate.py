"""Administrative handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient

from dokomoforms.handlers.util import BaseHandler
from dokomoforms.api import SurveyResource, SubmissionResource
from dokomoforms.models import Survey
from dokomoforms.models import ModelJSONEncoder
import json


class Enumerate(BaseHandler):
    def get(self, survey_id):                
        sr = SurveyResource()
        survey_model = self.session.query(Survey).get(survey_id)
        survey = sr.prepare(survey_model);
        print(survey['version'])
        print(survey['title'])
        self.render('survey.html',
                    survey_title=survey['title'],
                    survey=json.dumps(survey, cls=ModelJSONEncoder)),
