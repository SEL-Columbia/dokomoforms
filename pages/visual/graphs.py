import tornado.web
from db.answer import get_answers_for_question, get_geo_json

from pages.util.base import BaseHandler

from pages.util.visual import user_owns_question


class GraphVisualizationHandler(BaseHandler):
    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        self.render('view-graph-visualization.html', question_id=question_id)


class MapVisualizationHandler(BaseHandler):
    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        raw_answers = get_answers_for_question(question_id).fetchall()
        answers = list(map(get_geo_json, raw_answers))
        coordinates = list(map(lambda x: x['coordinates'], answers))
        self.render('view-map-visualization.html', question_id=question_id,
                    coordinates=coordinates)
