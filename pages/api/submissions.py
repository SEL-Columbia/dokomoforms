"""API endpoints dealing with submissions."""
from tornado.escape import json_encode, to_unicode

import api.submission
from pages.util.base import APIHandler, get_email


class SubmissionsAPIHandler(APIHandler):
    """The endpoint for getting all submissions to a survey."""

    def get(self, survey_id: str):
        subs = None
        if 'submitter' in self.request.arguments:
            subs = list(map(to_unicode, self.request.arguments['submitter']))
        response = api.submission.get_all(survey_id, email=get_email(self),
                                          submitters=subs)
        # self.set_header('Content-type', 'application/json')
        self.write(response)


class SingleSubmissionAPIHandler(APIHandler):
    """The endpoint for getting a single submission."""

    def get(self, submission_id: str):
        response = api.submission.get_one(submission_id, email=get_email(self))
        self.write(response)
