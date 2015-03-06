"""API endpoints dealing with aggregations."""
from tornado.escape import json_encode
import tornado.web
from dokomoforms.api import json_response

import dokomoforms.api.aggregation as aggregation_api
from dokomoforms.handlers.util.base import APIHandler, get_email, \
    validation_message


class AggregationHandler(APIHandler):
    def _apply_aggregation(self, aggregation_name: str, question_id: str):
        try:
            method = getattr(aggregation_api, aggregation_name)
            return method(self.db, question_id, email=get_email(self))
        except AttributeError:
            reason = json_encode(
                validation_message('aggregation', aggregation_name,
                                   'no_such_method'))
        except aggregation_api.InvalidTypeForAggregationError:
            reason = json_encode(
                validation_message('aggregation', aggregation_name,
                                   'invalid_type'))
        except aggregation_api.NoSubmissionsToQuestionError:
            reason = json_encode(
                validation_message('aggregation', aggregation_name,
                                   'no_submissions'))
        raise tornado.web.HTTPError(422, reason=reason)

    def get(self, question_id: str):
        response = [self._apply_aggregation(arg, question_id) for arg in
                    self.request.arguments]
        self.write(json_response(response))
