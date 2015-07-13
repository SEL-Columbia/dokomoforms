"""TornadoResource class for dokomoforms.models.survey.Survey."""
import os.path
import datetime

import restless.exceptions as exc

from sqlalchemy.sql.expression import func

from dokomoforms.api import BaseResource
from dokomoforms.api.submissions import _create_submission
from dokomoforms.models import (
    Survey, Submission, construct_survey_node,
    User,
    Node, construct_node
)


def _create_or_get_survey_node(session, node_dict):
    if 'id' in node_dict:
        node = session.query(Node).get(node_dict['id'])
        # TODO: raise an exception if node is None
    else:
        node = construct_node(**node_dict)
    return construct_survey_node(node=node)


class SurveyResource(BaseResource):

    """Restless resource for Surveys.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    resource_type = Survey
    default_sort_column_name = 'created_on'
    objects_key = 'surveys'

    http_methods = {
        'list': {
            'GET': 'list',
            'POST': 'create',
            'PUT': 'update_list',
            'DELETE': 'delete_list',
        },
        'detail': {
            'GET': 'detail',
            'POST': 'create_detail',
            'PUT': 'update',
            'DELETE': 'delete',
        },
        'list_submissions': {
            'GET': 'list_submissions'
        },
        'stats': {
            'GET': 'stats'
        },
        'activity': {
            'GET': 'activity'
        },
        'activity_all': {
            'GET': 'activity_all'
        },
        'submit': {
            'POST': 'submit'
        }
    }

    def is_authenticated(self):
        """GET detail is allowed unauthenticated."""
        # TODO: always allowed unauthenticated?
        uri = self.request.uri
        survey_id = uri.rstrip('/').split('/')[-1]
        detail_url = self.application.reverse_url('survey', survey_id)
        is_detail = uri == os.path.commonprefix((uri, detail_url))
        if self.request_method() == 'GET' and is_detail:
            return True
        return super().is_authenticated()

    def detail(self, survey_id):
        """Return the given survey.

        Enforces authentication for EnumeratorOnlySurvey.
        TODO: Check if that makes sense.
        """
        survey = super().detail(survey_id)
        if not super().is_authenticated() and survey.survey_type != 'public':
            raise exc.Unauthorized()
        return survey

    def create(self):
        """Create a new survey.

        Uses the current_user_model (i.e. logged-in user) as creator.
        """
        with self.session.begin():
            # create a list of Node models
            _node = _create_or_get_survey_node
            self.data['nodes'] = [
                _node(self.session, node) for node in self.data['nodes']
            ]
            self.data['creator'] = self.current_user_model
            # pass survey props as kwargs
            survey = Survey(**self.data)
            self.session.add(survey)

        return survey

    def submit(self, survey_id):
        """List all submissions for a survey."""
        survey = self.session.query(Survey).get(survey_id)
        if survey is None:
            raise exc.NotFound()
        return _create_submission(self, survey)

    def list_submissions(self, survey_id):
        """List all submissions for a survey."""
        response_list = self.list(where=(Survey.id == survey_id))

        response = {
            'survey_id': survey_id,
            'submissions': response_list
        }
        response = self._add_meta_props(response)
        return response

    def stats(self, survey_id):
        """Get stats for a survey."""
        result = (
            self.session
            .query(
                func.max(Survey.created_on),
                func.min(Submission.submission_time),
                func.max(Submission.submission_time),
                func.count(Submission.id),
            )
            .select_from(Submission)
            .join(Survey)
            # TODO: ask @jmwohl what this line is supposed to do
            # .filter(User.id == self.current_user_model.id)
            .filter(Submission.survey_id == survey_id)
            .one()
        )

        response = {
            "created_on": result[0],
            "earliest_submission_time": result[1],
            "latest_submission_time": result[2],
            "num_submissions": result[3]
        }
        return response

    def activity_all(self):
        """Get activity for all surveys."""
        days = int(self.r_handler.get_argument('days', 30))
        response = self._generate_activity_response(days)
        return response

    def activity(self, survey_id):
        """Get activity for a single survey."""
        days = int(self.r_handler.get_argument('days', 30))
        response = self._generate_activity_response(days, survey_id)
        return response

    def _generate_activity_response(self, days=30, survey_id=None):
        """Get the activity response.

        Build and execute the query for activity, specifying the number of days
        in the past from the current date to return.

        If a survey_id is specified, only activity from that
        survey will be returned.
        """
        user = self.current_user_model

        # number of days prior to return
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=days - 1)

        # truncate the datetime to just the day
        date_trunc = func.date_trunc('day', Submission.submission_time)

        query = (
            self.session
            .query(date_trunc, func.count())
            .filter(User.id == user.id)
            .filter(Submission.submission_time >= from_date)
        )

        if survey_id is not None:
            query = query.filter(Submission.survey_id == survey_id)

        query = (
            query
            .group_by(date_trunc)
            .order_by(date_trunc.desc())
        )

        # TODO: Figure out if this should use OrderedDict
        return {'activity': [
            {'date': date, 'num_submissions': num} for date, num in query
        ]}

    # def prepare(self, data):
    #     """Determine which fields to return.

    #     If we don't prep the data, all the fields get returned!

    #     We can subtract fields here if there are fields which shouldn't
    #     be included in the API.
    #     """
    #     return data
