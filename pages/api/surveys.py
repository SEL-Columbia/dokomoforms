"""API endpoints dealing with surveys."""

import json

import api.survey
from pages.util.base import APIHandler, get_email


class SurveysAPI(APIHandler):
    """The endpoint for getting all of a user's surveys."""

    def get(self):
        """
        I hope you like parentheses.

        """
        self.write(json.dumps(api.survey.get_all(get_email(self))))


class SingleSurveyAPI(APIHandler):
    """The endpoint for getting a single survey."""

    def get(self, survey_id: str):
        email = get_email(self)
        self.write(json.dumps(api.survey.get_one(survey_id, email=email)))
