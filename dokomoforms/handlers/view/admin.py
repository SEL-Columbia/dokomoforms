"""Admin view handlers."""

import tornado.web

from dokomoforms.models import Answer, Question, SurveyNode
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
        # TODO: should this be doine in JS?
        survey_stats = 'some stats?'
        question_stats = 'some stats?'
        survey = get_survey_for_handler(self, survey_id)
        self.render(
            'view_survey.html',
            survey=survey,
            question_stats=question_stats,
            survey_stats=survey_stats
        )


class ViewSurveyDataHandler(BaseHandler):

    """The endpoint for getting a single survey's data page."""

    @tornado.web.authenticated
    def get(self, survey_id: str):
        """GET the data page."""
        location_questions = []
        survey_stats = 'some stats?'
        question_stats = 'some stats?'
        for result in question_stats:
            # question = 'question'
            question_type = 'question_id'
            if question_type == 'location':
                question_id = 'question_id'
                # answers = 'answers'
                map_data = 'coord[0] coord[1] json_encode(submission)'
                location_questions.append({
                    'question_id': question_id,
                    'map_data': map_data,
                })

        survey = get_survey_for_handler(self, survey_id)
        self.render(
            'view_data.html',
            survey=survey,
            question_stats=question_stats,
            survey_stats=survey_stats,
            location_questions=location_questions
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
