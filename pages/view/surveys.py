"""Survey views."""

from tornado.escape import json_encode
import tornado.web

import api.survey
from pages.util.base import APIHandler, get_email, BaseHandler


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        surveys = json_encode(api.survey.get_all(get_email(self)))
