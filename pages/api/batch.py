"""API endpoints dealing with batch operations."""
import tornado.web
import api.batch
from db.survey import IncorrectQuestionIdError
from pages.util.base import APIHandler, catch_bare_integrity_error, \
    get_json_request_body, validation_message


class BatchSubmissionAPIHandler(APIHandler):
    @catch_bare_integrity_error
    def post(self, survey_id: str):
        data = get_json_request_body(self)

        if data.get('survey_id', None) != survey_id:
            reason = validation_message('submission', 'survey_id', 'invalid')
            raise tornado.web.HTTPError(422, reason=reason)
        try:
            self.write(api.batch.submit(self.db, data))
            self.set_status(201)
        except KeyError as e:
            reason = validation_message('submission', str(e), 'missing_field')
            raise tornado.web.HTTPError(422, reason=reason)
        except IncorrectQuestionIdError:
            reason = validation_message('submission', 'question_id', 'invalid')
            raise tornado.web.HTTPError(422, reason=reason)
