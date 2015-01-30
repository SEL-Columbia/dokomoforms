import functools

import tornado.web

from db.question import question_select
from db.survey import get_email_address


def user_owns_question(f):
    @functools.wraps(f)
    def wrapper(self, question_id: str, *args):
        question = question_select(question_id)
        authorized_email = get_email_address(question.survey_id)
        if self.current_user != authorized_email:
            raise tornado.web.HTTPError(404)
        return f(self, question_id, *args)

    return wrapper
