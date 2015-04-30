"""Submission views."""
import tornado.web

from dokomoforms.db.survey import survey_select
from dokomoforms.handlers.util.base import BaseHandler
import dokomoforms.api.submission as submission_api


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
