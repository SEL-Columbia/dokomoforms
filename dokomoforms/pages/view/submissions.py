"""Submission views."""
import tornado.web

from dokomoforms.db.submission import get_submissions_by_email
from dokomoforms.db.survey import survey_select
from dokomoforms.pages.util.base import BaseHandler
import dokomoforms.api.submission as submission_api
import dokomoforms.api.aggregation as aggregation_api


class ViewSubmissionsHandler(BaseHandler):
    """The endpoint for getting all submissions to a survey."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        submissions = get_submissions_by_email(self.db, survey_id,
                                               self.current_user)
        stats = aggregation_api.get_question_stats
        question_stats = stats(self.db, survey_id, email=self.current_user)
        survey = survey_select(self.db, survey_id, email=self.current_user)
        self.render('view-submissions.html', message=None, survey=survey,
                    submissions=submissions, question_stats=question_stats)


class ViewSubmissionHandler(BaseHandler):
    """The endpoint for viewing a submission."""

    @tornado.web.authenticated
    def get(self, submission_id: str):
        submission = submission_api.get_one(self.db, submission_id,
                                            self.current_user)['result']
        survey = survey_select(self.db, submission['survey_id'],
                               email=self.current_user)
        self.render('view-submission.html', message=None, survey=survey,
                    submission=submission)
