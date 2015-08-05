"""Admin view handlers."""
import tornado.web

import sqlalchemy as sa

from dokomoforms.models import (
    Answer, Question, SurveyNode, generate_question_stats, jsonify
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
            result = {
                'survey_node_id': survey_node.id,
                'map_data': [
                    {
                        'submission_id': answer.submission_id,
                        'coordinates': answer.response['response'],
                    } for answer in answers
                ],
            }
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


class VisualizationHandler(BaseHandler):

    """Visualize answers to a SurveyNode or Question."""

    @tornado.web.authenticated
    def get(self, question_or_survey_node_id: str):
        """GET data visualizations for a SurveyNode or Question."""
        mystery = question_or_survey_node_id
        question = self.session.query(Question).get(mystery)
        survey_node = self.session.query(SurveyNode).get(mystery)
        node = question or survey_node

        if node is None:
            raise tornado.web.HTTPError(404)

        if isinstance(node, Question):
            where_id = Answer.question_id == mystery
            type_constraint = node.type_constraint
        else:
            where_id = Answer.survey_node_id == mystery
            type_constraint = node.the_type_constraint

        answer_cls = ANSWER_TYPES[type_constraint]
        where = sa.and_(where_id, answer_cls.main_answer.isnot(None))

        time_data, bar_data, map_data = None, None, None
        if type_constraint in {'integer', 'decimal'}:
            time_data = [
                [save_time.isoformat(), jsonify(value)]
                for save_time, value in self.session.execute(
                    sa.select([Answer.save_time, answer_cls.main_answer])
                    .select_from(Answer.__table__.join(
                        answer_cls.__table__, Answer.id == answer_cls.id
                    ))
                    .where(where)
                    .order_by(Answer.save_time.asc())
                )
            ]

        bar_graph_types = {
            'text', 'integer', 'decimal', 'date', 'time', 'timestamp',
            'multiple_choice'
        }
        if type_constraint in bar_graph_types:
            bar_data = [
                [jsonify(value), count]
                for value, count in self.session.execute(
                    sa.select([
                        answer_cls.main_answer,
                        sa.func.count(answer_cls.main_answer)
                    ])
                    .select_from(Answer.__table__.join(
                        answer_cls.__table__, Answer.id == answer_cls.id
                    ))
                    .where(where)
                    .group_by(answer_cls.main_answer)
                    .order_by(answer_cls.main_answer)
                )
            ]

        if type_constraint in {'location', 'facility'}:
            map_data = [
                {
                    'submission_id': answer.submission_id,
                    'coordinates': answer.response['response']
                }
                for answer in (
                    self.session
                    .query(answer_cls)
                    .filter(where)
                )
            ]

        self.render(
            'view_visualize.html',
            time_data=time_data,
            bar_data=bar_data,
            map_data=map_data,
        )
