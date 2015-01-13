"""Survey views."""

import tornado.web

from db.survey import get_surveys_for_user_by_email
from pages.util.base import BaseHandler


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        surveys = get_surveys_for_user_by_email(self.current_user)
        self.render('view.html', message=None, surveys=surveys)
