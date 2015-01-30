import tornado.web

from pages.util.base import BaseHandler

from pages.util.visual import user_owns_question


class VisualizationHandler(BaseHandler):
    @tornado.web.authenticated
    @user_owns_question
    def get(self, question_id: str):
        self.render('view-visualization.html', question_id=question_id)
