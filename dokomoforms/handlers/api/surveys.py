"""API endpoints dealing with surveys."""

import dokomoforms.api.survey as survey_api
import dokomoforms.api.submission as submission_api
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


class SurveySubmissionsAPIHandler(APIHandler):
    """The endpoint for getting all submissions to a survey."""

    def _get_subs(self):
        if 'submitter' in self.request.arguments:
            return list(map(to_unicode, self.request.arguments['submitter']))

    def get(self, survey_id: str):
        filters = self.get_argument('filters', None)
        order_by = self.get_argument('order_by', 'submission_time')
        direction = self.get_argument('direction', 'DESC')
        limit = self.get_argument('limit', None)
        subs = self._get_subs()
        response = submission_api.get_all(
            self.db,
            survey_id=survey_id,
            email=self.get_email(),
            submitters=subs,
            filters=filters,
            order_by=order_by,
            direction=direction,
            limit=limit
        )
        self.write(response)

    def post(self, survey_id: str):
        body = get_json_request_body(self)
        subs = body.get('submitters', None)
        filters = body.get('filters', None)
        order_by = body.get('order_by', None)
        direction = body.get('direction', 'ASC')
        limit = body.get('limit', None)
        response = submission_api.get_all(
            self.db,
            survey_id,
            email=self.get_email(),
            submitters=subs,
            filters=filters,
            order_by=order_by,
            direction=direction,
            limit=limit
        )
        self.write(response)

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
