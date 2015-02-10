import tornado.web
from sqlalchemy.engine import ResultProxy
from tornado.escape import json_encode

import api.submission
from api.aggregation import time_series, bar_graph, \
    NoSubmissionsToQuestionError
from db.answer import get_geo_json, get_answers_for_question
from db.question import question_select
from pages.util.base import BaseHandler, user_owns_question


class VisualizationHandler(BaseHandler):
    # TODO: consider absorbing this into api.aggregation
    def _get_map_data(self, raw_answers: ResultProxy):
        for raw_answer in raw_answers:
            coord = get_geo_json(raw_answer)['coordinates']
            sub_id = raw_answer.submission_id
            subs = api.submission.get_one(sub_id, email=self.current_user)
            yield [coord[0], coord[1], json_encode(subs['result'])]


    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        question = question_select(question_id)
        answers = get_answers_for_question(question_id)
        time_data, bar_data, map_data = None, None, None
        if question.type_constraint_name in {'integer', 'decimal'}:
            try:
                data = time_series(question_id, email=self.current_user)
                time_data = data['result']
            except NoSubmissionsToQuestionError:
                pass
        if question.type_constraint_name in {'text', 'integer', 'decimal',
                                             'date', 'time', 'location',
                                             'multiple_choice'}:
            try:
                data = bar_graph(question_id, email=self.current_user)
                bar_data = data['result']
            except NoSubmissionsToQuestionError:
                pass
        if question.type_constraint_name == 'location':
            map_data = list(self._get_map_data(answers))
        self.render('visualization.html', time_data=time_data,
                    bar_data=bar_data,
                    map_data=map_data)
