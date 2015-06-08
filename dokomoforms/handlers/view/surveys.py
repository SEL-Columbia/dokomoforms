"""Survey views."""

import tornado.web
from sqlalchemy.engine import ResultProxy
from tornado.escape import json_encode

from dokomoforms.handlers.util.base import BaseHandler, user_owns_question
from dokomoforms.api.survey import get_stats
import dokomoforms.api.submission as submission_api
from dokomoforms.api.aggregation import time_series, get_question_stats
from dokomoforms.db.survey import survey_select
from dokomoforms.db.answer import get_geo_json, get_answers_for_question


class ViewHandler(BaseHandler):

    """The endpoint for getting all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        self.render('view.html', message=None)


class ViewSurveyHandler(BaseHandler):

    """The endpoint for getting a single survey's administration page."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        survey_stats = get_stats(self.db, survey_id, email=self.current_user)
        question_stats = get_question_stats(
            self.db, survey_id, email=self.current_user)
        survey = survey_select(self.db, survey_id, email=self.current_user)
        self.render('view-survey.html', message=None, survey=survey,
                    question_stats=question_stats, survey_stats=survey_stats)


class ViewSurveyDataHandler(BaseHandler):

    """The endpoint for getting a single survey's data page."""

    # TODO: consider absorbing this into api.aggregation
    def _get_map_data(self, raw_answers: ResultProxy):
        for raw_answer in raw_answers:
            coord = get_geo_json(self.db, raw_answer)['coordinates']
            sub_id = raw_answer.submission_id
            subs = submission_api.get_one(self.db, sub_id,
                                          email=self.current_user)
            yield [coord[0], coord[1], json_encode(subs['result'])]

    @tornado.web.authenticated
    def get(self, survey_id: str):
        location_questions = []
        survey_stats = get_stats(self.db, survey_id, email=self.current_user)
        question_stats = get_question_stats(
            self.db, survey_id, email=self.current_user)
        for result in question_stats['result']:
            question = result['question']
            question_type = question[6]
            if question_type == "location":
                question_id = question[0]
                answers = get_answers_for_question(self.db, question_id)
                map_data = list(self._get_map_data(answers))
                location_questions.append({
                    "question_id": question_id,
                    "map_data": map_data
                })

        survey = survey_select(self.db, survey_id, email=self.current_user)
        self.render('view-survey-data.html', message=None, survey=survey,
                    question_stats=question_stats, survey_stats=survey_stats,
                    location_questions=location_questions)
