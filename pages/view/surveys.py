"""Survey views."""

import tornado.web

from db.submission import get_number_of_submissions

from db.survey import get_surveys_by_email
from pages.util.base import BaseHandler


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        surveys = get_surveys_by_email(self.db, self.current_user)
        num_sub = (get_number_of_submissions(self.db,
                                             s.survey_id) for s in surveys)
        surveys_with_num = zip(surveys, num_sub)
        self.render('view.html', message=None, surveys=surveys_with_num)
