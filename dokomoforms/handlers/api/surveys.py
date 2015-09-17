"""TornadoResource class for dokomoforms.models.survey.Survey."""
import os.path
import datetime

import restless.exceptions as exc
from restless.constants import CREATED

from sqlalchemy import cast, Date
from sqlalchemy.sql import func

from dokomoforms.handlers.api import BaseResource
from dokomoforms.handlers.api.submissions import (
    SubmissionResource, _create_submission
)
from dokomoforms.models import (
    Survey, Submission, SubSurvey, Choice,
    construct_survey, construct_survey_node, construct_bucket,
    administrator_filter, get_model,
    Node, construct_node
)
from dokomoforms.models.survey import _administrator_table


# TODO: clean up this mess
def _create_sub_survey(session, sub_survey_dict, parent_node):
    for bucket_dict in sub_survey_dict['buckets']:
        if bucket_dict['bucket_type'] == 'multiple_choice':
            choice_dict = bucket_dict['bucket']
            choice_number = choice_dict.pop('choice_number', None)
            if choice_number is not None:
                bucket_dict['bucket'] = parent_node.choices[choice_number]
            choice_id = choice_dict.pop('choice_id', None)
            if choice_id is not None:
                bucket_dict['bucket'] = session.query(Choice).get(choice_id)
    sub_survey_dict['buckets'] = [
        construct_bucket(**b) for b in sub_survey_dict['buckets']
    ]
    repeatable = sub_survey_dict.get('repeatable', None)
    _cogsn = _create_or_get_survey_node
    sub_survey_dict['nodes'] = [
        _cogsn(session, node, repeatable) for node in sub_survey_dict['nodes']
    ]
    return SubSurvey(**sub_survey_dict)


def _create_or_get_survey_node(session, survey_node_dict, repeatable=None):
    node_dict = survey_node_dict['node']
    if 'id' in node_dict:
        node = get_model(session, Node, node_dict['id'])
    else:
        choices = node_dict.get('choices', None)
        if choices is not None:
            node_dict['choices'] = [
                Choice(**choice) for choice in choices
            ]
        node = construct_node(**node_dict)
    survey_node_dict['node'] = node
    if repeatable is not None:
        survey_node_dict['repeatable'] = repeatable
    _css = _create_sub_survey
    sub_survey_data = survey_node_dict.get('sub_surveys', None)
    if sub_survey_data is not None:
        survey_node_dict['sub_surveys'] = [
            _css(session, ssd, node) for ssd in sub_survey_data
        ]
    return construct_survey_node(**survey_node_dict)


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

    def __init__(self, *args, **kwargs):
        """Make submit return 201."""
        super().__init__(*args, **kwargs)
        self.status_map['submit'] = CREATED

    def is_authenticated(self):
        """GET detail is allowed unauthenticated."""
        # TODO: always allowed unauthenticated?
        uri = self.request.uri
        request_method = self.request_method()
        if request_method == 'GET':
            survey_id_index = -1
            url_name = 'survey'
        elif request_method == 'POST':
            survey_id_index = -2
            url_name = 'submit_to_survey'
        if request_method in {'GET', 'POST'}:
            survey_id = uri.rstrip('/').split('/')[survey_id_index]
            url = self.application.reverse_url(url_name, survey_id)
            if uri == os.path.commonprefix((uri, url)):
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
            survey = construct_survey(**self.data)
            self.session.add(survey)

        return survey

    def submit(self, survey_id):
        """Submit to a survey."""
        return _create_submission(self, self._get_model(survey_id))

    def list_submissions(self, survey_id):
        """List all submissions for a survey."""
        sub_resource = SubmissionResource()
        sub_resource.ref_rh = self.ref_rh
        sub_resource.request = self.request
        sub_resource.application = self.application
        where = Submission.survey_id == survey_id
        result = sub_resource.list(where=where)
        response = sub_resource.wrap_list_response(result)
        if sub_resource.content_type == 'csv':
            title = (
                self.session
                .query(Survey.title[Survey.default_language])
                .filter_by(id=survey_id)
                .scalar()
            )
            self._set_filename('survey_{}_submissions'.format(title), 'csv')
        elif sub_resource.content_type == 'json':
            response['total_entries'] = (
                self.session
                .query(func.count(Submission.id))
                .filter_by(survey_id=survey_id)
                .scalar()
            )
            response['survey_id'] = survey_id
        return response

    def stats(self, survey_id):
        """Get stats for a survey."""
        result = (
            self.session
            .query(
                func.max(Survey.created_on),
                func.min(Submission.save_time),
                func.max(Submission.save_time),
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
        user_id = self.r_handler.get_argument('user_id', None)
        response = self._generate_activity_response(days, user_id=user_id)
        return response

    def activity(self, survey_id):
        """Get activity for a single survey."""
        days = int(self.r_handler.get_argument('days', 30))
        response = self._generate_activity_response(days, survey_id=survey_id)
        return response

    def _generate_activity_response(self,
                                    days=30, user_id=None, survey_id=None):
        """Get the activity response.

        Build and execute the query for activity, specifying the number of days
        in the past from the current date to return.

        If a survey_id is specified, only activity from that
        survey will be returned.
        """
        # number of days prior to return
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=days - 1)

        # truncate the datetime to just the day
        submission_date = (
            cast(Submission.save_time, Date).label('submission_date')
        )

        query = self.session.query(submission_date, func.count())

        if user_id is not None:
            query = (
                query
                .join(Survey.submissions)
                .outerjoin(_administrator_table)
                .filter(administrator_filter(user_id))
            )

        query = query.filter(Submission.save_time >= from_date)

        if survey_id is not None:
            query = query.filter(Submission.survey_id == survey_id)

        query = (
            query
            .group_by('submission_date')
            .order_by(submission_date.desc())
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


def get_survey_for_handler(tornado_handler, survey_id):
    """Maybe a handler needs a survey from the API."""
    survey_resource = SurveyResource()
    survey_resource.ref_rh = tornado_handler
    survey_resource.request = tornado_handler.request
    survey_resource.application = tornado_handler.application
    return survey_resource.detail(survey_id)
