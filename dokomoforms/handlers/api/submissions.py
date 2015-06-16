"""Submissions API handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient
from tornado.escape import json_decode, json_encode

from dokomoforms.handlers.util import BaseAPIHandler


class SubmissionsAPIList(BaseAPIHandler):
    def get(self, survey_id=None):
        self.write(json_encode([]))

    def post(self):
        pass

    def put(self, survey_id):
        pass

    def delete(self, survey_id):
        pass
