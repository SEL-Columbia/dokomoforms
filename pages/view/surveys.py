"""Survey views."""

import tornado.web

from db.submission import get_number_of_submissions, get_submissions_by_email

from db.survey import get_surveys_by_email, survey_select
from pages.util.base import BaseHandler


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        surveys = get_surveys_by_email(self.current_user)
        num_sub = (get_number_of_submissions(s.survey_id) for s in surveys)
        surveys_with_num = zip(surveys, num_sub)
        self.render('view.html', message=None, surveys=surveys_with_num)


class ViewSubmissionsHandler(BaseHandler):
    """The endpoint for getting all submissions to a survey."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        submissions = get_submissions_by_email(survey_id, self.current_user)
        survey = survey_select(survey_id, email=self.current_user)
        self.render('view-submissions.html', message=None, survey=survey,
                    submissions=submissions)
