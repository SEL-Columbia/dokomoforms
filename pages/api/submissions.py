"""API endpoints dealing with submissions."""
from tornado.escape import json_encode, to_unicode

import api.submission
from pages.util.base import APIHandler, get_email, get_json_request_body


class SubmissionsAPIHandler(APIHandler):
    """The endpoint for getting all submissions to a survey."""

    def _get_subs(self):
        if 'submitter' in self.request.arguments:
            return list(map(to_unicode, self.request.arguments['submitter']))

    def get(self, survey_id: str):
        subs = self._get_subs()
        response = api.submission.get_all(survey_id,
                                          email=get_email(self),
                                          submitters=subs)
        self.write(response)

    def post(self, survey_id: str):
        body = get_json_request_body(self)
        subs = body['submitters']
        filters = body['filters']
        response = api.submission.get_all(survey_id,
                                          email=get_email(self),
                                          submitters=subs,
                                          filters=filters)
        self.write(response)


class SingleSubmissionAPIHandler(APIHandler):
    """The endpoint for getting a single submission."""

    def get(self, submission_id: str):
        response = api.submission.get_one(submission_id, email=get_email(self))
        self.write(response)
