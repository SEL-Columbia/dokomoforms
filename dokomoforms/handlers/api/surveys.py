"""API endpoints dealing with surveys."""

import dokomoforms.api.survey as survey_api
from dokomoforms.handlers.util.base import APIHandler, \
    catch_bare_integrity_error, get_json_request_body


class SurveysAPIHandler(APIHandler):
    """The endpoint for getting all of a user's surveys."""

    def get(self):
        """I hope you like parentheses."""
        self.write(survey_api.get_all(self.db, self.get_email()))


class SingleSurveyAPIHandler(APIHandler):
    """The endpoint for getting a single survey."""

    def get(self, survey_id: str):
        email = self.get_email()
        self.write(survey_api.get_one(self.db, survey_id, email=email))


class SurveyStatsAPIHandler(APIHandler):
    """The endpoint for getting statistics about a survey."""

    def get(self, survey_id: str):
        email = self.get_email()
        self.write(survey_api.get_stats(self.db, survey_id, email=email))


class CreateSurveyAPIHandler(APIHandler):
    """The endpoint for creating a survey."""

    @catch_bare_integrity_error
    def post(self):
        data = get_json_request_body(self)
        self.write(survey_api.create(self.db, data))
        self.set_status(201)
