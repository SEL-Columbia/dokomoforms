"""Survey views."""

import tornado.web

from dokomoforms.handlers.util.base import BaseHandler
from dokomoforms.api.survey import get_stats
from dokomoforms.db.survey import survey_select
import dokomoforms.api.aggregation as aggregation_api


class ViewHandler(BaseHandler):
    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        self.render('view.html', message=None)


class ViewSurveyHandler(BaseHandler):
    """The endpoint for getting a single survey's administration page."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        stats = aggregation_api.get_question_stats
        survey_stats = get_stats(self.db, survey_id, email=self.current_user)
        question_stats = stats(self.db, survey_id, email=self.current_user)
        survey = survey_select(self.db, survey_id, email=self.current_user)
        self.render('view-survey.html', message=None, survey=survey,
                    question_stats=question_stats, survey_stats=survey_stats)


class ViewSurveyDataHandler(BaseHandler):
    """The endpoint for getting a single survey's data page."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        stats = aggregation_api.get_question_stats
        survey_stats = get_stats(self.db, survey_id, email=self.current_user)
        question_stats = stats(self.db, survey_id, email=self.current_user)
        survey = survey_select(self.db, survey_id, email=self.current_user)
        self.render('view-survey-data.html', message=None, survey=survey,
                    question_stats=question_stats, survey_stats=survey_stats)
