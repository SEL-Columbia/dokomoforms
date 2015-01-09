"""API endpoints dealing with submissions."""
from tornado.escape import json_encode

import api.submission
from pages.util.base import APIHandler, get_email


class SubmissionsAPI(APIHandler):
    """The endpoint for getting all submissions to a survey."""

    def get(self, survey_id: str):
        response = api.submission.get_all(survey_id, email=get_email(self))
        self.write(json_encode(response))


class SingleSubmissionAPI(APIHandler):
    """The endpoint for getting a single submission."""

    def get(self, submission_id: str):
        response = api.submission.get_one(submission_id, email=get_email(self))
        self.write(json_encode(response))
