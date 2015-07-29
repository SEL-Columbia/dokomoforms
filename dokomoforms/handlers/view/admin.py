"""Admin view handlers."""

import tornado.web

from dokomoforms.models import (
    Answer, Question, SurveyNode, generate_question_stats
)
from dokomoforms.models.answer import ANSWER_TYPES
from dokomoforms.handlers.util import BaseHandler
from dokomoforms.api import get_survey_for_handler, get_submission_for_handler


class ViewHandler(BaseHandler):

    """Get all of a user's surveys."""

    @tornado.web.authenticated
    def get(self):
        """GET a dashboard-like view."""
        self.render('view_view.html')


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
            yield {
                'survey_node_id': survey_node.id,
                'map_data': [
                    {
                        'submission_id': answer.submission_id,
                        'coordinates': answer.response['response'],
                    } for answer in answers
                ],
            }

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


class VisualizationHandler(BaseHandler):

    """Visualize answers to a SurveyNode or Question."""

    def get(self, question_or_survey_node_id: str):
        """GET data visualizations for a SurveyNode or Question."""
        mystery_id = question_or_survey_node_id
        is_question = True
        node = self.session.query(Question).get(mystery_id)
        if node is None:
            is_question = False
            node = self.session.query(SurveyNode).get(mystery_id)

        answers = self.session.query(Answer)
        if is_question:
            answers = answers.filter_by(question_id=mystery_id)
        else:
            answers = answers.filter_by(survey_node_id=mystery_id)
        answers = answers.all()

        time_data = None
        if node.type_constraint in {'integer', 'decimal'}:
            time_data = 'time series'

        bar_data = None
        bar_data_types = {
            'text', 'integer', 'decimal', 'date', 'time', 'timestamp',
            'location', 'multiple_choice'  # facility?
        }
        if node.type_constraint in bar_data_types:
            bar_data = 'bar data'

        map_data = None
        if node.type_constraint in {'location', 'facility'}:
            map_data = 'map_data'

        self.render(
            'view_visualize.html',
            time_data=time_data,
            bar_data=bar_data,
            map_data=map_data,
        )
