"""Admin view handlers."""
import tornado.web

from dokomoforms.models import generate_question_stats
from dokomoforms.models.answer import ANSWER_TYPES
from dokomoforms.handlers.util import BaseHandler
from dokomoforms.handlers.api import (
    get_survey_for_handler, get_submission_for_handler
)


class ViewSurveyHandler(BaseHandler):

    """The endpoint for getting a single survey's admin page."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        """GET the admin page."""
        # TODO: should this be done in JS?
        survey = get_survey_for_handler(self, survey_id)
        self.render(
            'view_survey.html',
            survey=survey,
        )


class ViewSurveyDataHandler(BaseHandler):

    """The endpoint for getting a single survey's data page."""

    def _get_map_data(self, survey_nodes):
        for survey_node in survey_nodes:
            if survey_node.type_constraint not in {'location', 'facility'}:
                continue
            answer_cls = ANSWER_TYPES[survey_node.type_constraint]
            answers = (
                self.session
                .query(answer_cls)
                .filter_by(survey_node_id=survey_node.id)
                .filter(answer_cls.main_answer.isnot(None))
            )
            result = {
                'survey_node_id': survey_node.id
            }
            if survey_node.type_constraint == 'location':
                result['map_data'] = [
                    {
                        'submission_id': answer.submission_id,
                        'coordinates': answer.response['response'],
                    } for answer in answers
                ]
            if survey_node.type_constraint == 'facility':
                result['map_data'] = [
                    {
                        'submission_id': answer.submission_id,
                        'facility_name':
                            answer.response['response']['facility_name'],
                        'coordinates': {
                            'lat': answer.response['response']['lat'],
                            'lng': answer.response['response']['lng']}
                    } for answer in answers
                ]
            yield result  # pragma: no branch

    @tornado.web.authenticated
    def get(self, survey_id: str):
        """GET the data page."""
        survey = get_survey_for_handler(self, survey_id)
        question_stats = list(generate_question_stats(survey))
        location_stats = self._get_map_data(
            stat['survey_node'] for stat in question_stats
        )
        self.render(
            'view_data.html',
            survey=survey,
            question_stats=question_stats,
            location_stats=location_stats,
        )


class ViewSubmissionHandler(BaseHandler):

    """The endpoint for viewing a submission."""

    @tornado.web.authenticated
    def get(self, submission_id: str):
        """GET the visualization page."""
        submission = get_submission_for_handler(self, submission_id)
        survey = get_survey_for_handler(self, submission.survey_id)
        self.render(
            'view_submission.html', survey=survey, submission=submission
        )


class ViewUserAdminHandler(BaseHandler):

    """The endpoint for getting the user administration admin page."""

    @tornado.web.authenticated
    def get(self):
        """GET the user admin page."""
        # TODO: we could bootstrap with the initial data here, probably
        # not worth it.
        self.render(
            'view_user_admin.html'
        )
