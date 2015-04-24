"""API endpoints dealing with submissions."""
from tornado.escape import to_unicode
import tornado.web

import dokomoforms.api.submission as submission_api
from dokomoforms.db.survey import IncorrectQuestionIdError
from dokomoforms.handlers.util.base import APIHandler, get_json_request_body, \
    catch_bare_integrity_error, validation_message, APINoLoginHandler


class SubmissionsAPIHandler(APIHandler):
    """The endpoint for getting all submissions to all surveys."""

    def _get_subs(self):
        if 'submitter' in self.request.arguments:
            return list(map(to_unicode, self.request.arguments['submitter']))

    def get(self):
        survey_id = self.get_argument('survey_id', None)
        filters = self.get_argument('filters', None)
        order_by = self.get_argument('order_by', 'submission_time')
        direction = self.get_argument('direction', 'DESC')
        limit = self.get_argument('limit', None)
        subs = self._get_subs()
        response = submission_api.get_all(
            self.db,
            survey_id=survey_id,
            email=self.get_email(),
            submitters=subs,
            filters=filters,
            order_by=order_by,
            direction=direction,
            limit=limit
        )
        self.write(response)

    def post(self, survey_id: str):
        body = get_json_request_body(self)
        subs = body.get('submitters', None)
        filters = body.get('filters', None)
        order_by = body.get('order_by', None)
        direction = body.get('direction', 'ASC')
        limit = body.get('limit', None)
        response = submission_api.get_all(
            self.db,
            self.get_email(),
            survey_id=survey_id,
            submitters=subs,
            filters=filters,
            order_by=order_by,
            direction=direction,
            limit=limit
        )
        self.write(response)


class SubmissionActivityAPIHandler(APIHandler):
    """The endpoint for getting submission activity to a survey."""

    def get(self, survey_id: str=None):
        # TODO: HTTP 422 if the survey doesn't exist
        response = submission_api.get_activity(
            self.db, self.get_email(), survey_id
        )
        self.write(response)


class SingleSubmissionAPIHandler(APIHandler):
    """The endpoint for getting a single submission."""

    def get(self, submission_id: str):
        response = submission_api.get_one(
            self.db, submission_id, email=self.get_email())
        self.write(response)


class SubmitAPIHandler(APINoLoginHandler):
    """The endpoint for submitting to a survey. You don't need to log in to
    submit through the browser."""

    @catch_bare_integrity_error
    def post(self, survey_id: str):
        data = get_json_request_body(self)

        if data.get('survey_id', None) != survey_id:
            reason = validation_message('submission', 'survey_id', 'invalid')
            raise tornado.web.HTTPError(422, reason=reason)
        try:
            self.write(submission_api.submit(self.db, data))
            self.set_status(201)
        except KeyError as e:
            reason = validation_message('submission', str(e), 'missing_field')
            raise tornado.web.HTTPError(422, reason=reason)
        except IncorrectQuestionIdError:
            reason = validation_message('submission', 'question_id', 'invalid')
            raise tornado.web.HTTPError(422, reason=reason)
