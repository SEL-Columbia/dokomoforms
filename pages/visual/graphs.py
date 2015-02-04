from sqlalchemy.engine import ResultProxy
from tornado.escape import json_encode
import tornado.web
from db.answer import get_answers_for_question, get_geo_json
from db.question import question_select

from pages.util.base import BaseHandler

from pages.util.visual import user_owns_question

import api.submission


class GraphVisualizationHandler(BaseHandler):
    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        question = question_select(question_id)
        self.render('view-graph-visualization.html', question=question)


class MapVisualizationHandler(BaseHandler):
    def _get_map_data(self, raw_answers: ResultProxy):
        for raw_answer in raw_answers:
            coord = get_geo_json(raw_answer)['coordinates']
            sub_id = raw_answer.submission_id
            subs = api.submission.get_one(sub_id, email=self.current_user)
            yield [coord[0], coord[1], json_encode(subs['result'])]


    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        answers = get_answers_for_question(question_id).fetchall()
        coords_and_subs = list(self._get_map_data(answers))
        self.render('view-map-visualization.html', question_id=question_id,
                    coordinates_and_submissions=coords_and_subs)
