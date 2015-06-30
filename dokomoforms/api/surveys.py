import datetime
import tornado.web

from restless.preparers import FieldsPreparer
import restless.exceptions as exc
from restless.resources import skip_prepare

from sqlalchemy.sql.expression import func

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, construct_survey_node,
    User, construct_submission, construct_answer,
    Node, construct_node
)


class SurveyResource(BaseResource):
    """
    Restless resource for Surveys.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'surveys'

    # The preparer defines the fields that get returned.
    #preparer = FieldsPreparer(fields={
    #    'id': 'id',
    #    'deleted': 'deleted',
    #    'title': 'title',
    #    'default_language': 'default_language',
    #    'enumerator_only': 'enumerator_only',
    #    'version': 'version',
    #    'creator_id': 'creator_id',
    #    'creator_name': 'creator.name',
    #    'metadata': 'survey_metadata',
    #    'created_on': 'created_on',
    #    'last_update_time': 'last_update_time',
    #    'nodes': 'nodes',
    #})

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

    # GET /api/surveys/
    def list(self):
        """Return a list of surveys."""
        response = self._generate_list_response(Survey)
        return response

    # GET /api/surveys/<survey_id>
    def detail(self, survey_id):
        """Return a single survey."""
        survey = self.session.query(Survey).get(survey_id)
        if survey is None:
            raise exc.NotFound()
        else:
            return survey

    # POST /api/surveys/
    def create(self):
        """
        Create a new survey using the current_user_model (i.e. logged-in user)
        as creator.

        Since this captures all POST requests, we first check for a _method
        query param and treat the request accordingly.
        """
        if self.current_user_model is None:
            raise tornado.web.HTTPError(
                403,
                reason=(
                    'You do not have sufficient privilages.'
                ),
            )

        # Check for _method query param
        _method = self.r_handler.get_argument('_method', None)
        if _method is not None:
            if _method == 'DELETE':
                # treat this as a DELETE request:
                self.delete()

        def create_or_get_survey_node(node_dict):
            # pass node props as kwargs
            if 'id' in node_dict:
                node = self.session.query(Node).get(node_dict['id'])
            else:
                node = construct_node(**node_dict)
            return node

        with self.session.begin():
            # create a list of Node models
            nodes = list(map(create_or_get_survey_node, self.data['nodes']))
            # remove the existing nodes key from the received data
            del self.data['nodes']
            creator = self.current_user_model
            # pass survey props as kwargs
            survey = Survey(**self.data)
            # add the node models
            survey.nodes = nodes
            # add the survey to the creator
            creator.surveys.append(survey)

        return survey

    # PUT /api/surveys/<survey_id>/
    def update(self, survey_id):
        """TODO: how should this behave?"""
        survey = self.session.query(Survey).get(survey_id)

        if not survey:
            raise exc.NotFound()
        else:
            with self.session.begin():
                survey.update(self.data)
            return survey

    # DELETE /api/surveys/<survey_id>/
    def delete(self, survey_id):
        """
        Marks the survey.deleted = True. Does NOT remove the survey
        from the DB.
        """
        with self.session.begin():
            survey = self.session.query(Survey).get(survey_id)
            if not survey:
                raise exc.NotFound()
            else:
                survey.deleted = True

    # POST /api/surveys/<survey_id>/submit
    @skip_prepare
    def submit(self, survey_id):
        """
        List all submissions for a survey.
        """
        survey = self.session.query(Survey).get(survey_id)
        if survey is None:
            raise exc.BadRequest(
                "The survey could not be found."
            )

        # If an enumerator ID is present, add the enumerator
        if 'enumerator_user_id' in self.data:
            enumerator = self.session.query(
                User).get(self.data['enumerator_user_id'])
            self.data['enumerator'] = enumerator

        self.data['survey'] = survey

        with self.session.begin():
            # create a list of Answer models
            if 'answers' in self.data:
                answers = list(map(construct_answer, self.data['answers']))
                # remove the existing answers key from the received data
                del self.data['answers']

            # pass submission props as kwargs
            if 'submission_type' not in self.data:
                # by default fall to authenticate (i.e. EnumOnlySubmission)
                self.data['submission_type'] = 'authenticated'

            submission = construct_submission(**self.data)

            # add the answer models
            if 'answers' in self.data:
                submission.answers = answers

            # add the submission
            self.session.add(submission)

        return submission

    # GET /api/surveys/<survey_id>/submissions
    @skip_prepare
    def list_submissions(self, survey_id):
        """
        List all submissions for a survey.
        """
        response_list = self._generate_list_response(
            Submission, filter=(Survey.id == survey_id))

        response = {
            'survey_id': survey_id,
            'submissions': response_list
        }
        response = self._add_meta_props(response)
        return response

    # GET /api/surveys/<survey_id>/stats
    @skip_prepare
    def stats(self, survey_id):
        """
        Get stats for a survey.
        """
        user = self.current_user_model
        if user is None:
            raise exc.Unauthorized()

        result = self.session.\
            query(func.max(Survey.created_on),
                  func.min(Submission.submission_time),
                  func.max(Submission.submission_time),
                  func.count(Submission.id)).\
            select_from(Submission).\
            join(Submission.survey).\
            filter(User.id == user.id).\
            filter(Submission.survey_id == survey_id).one()

        response = {
            "created_on": result[0],
            "earliest_submission_time": result[1],
            "latest_submission_time": result[2],
            "num_submissions": result[3]
        }
        return response

    # GET /api/surveys/activity
    @skip_prepare
    def activity_all(self):
        """
        Get activity for all surveys.
        """
        days = int(self.r_handler.get_argument('days', 30))
        response = self._generate_activity_response(days)
        return response

    # GET /api/surveys/<survey_id>/activity
    @skip_prepare
    def activity(self, survey_id):
        """
        Get activity for a single survey.
        """
        days = int(self.r_handler.get_argument('days', 30))
        response = self._generate_activity_response(days, survey_id)
        return response

    def _generate_activity_response(self, days=30, survey_id=None):
        """
        Build and execute the query for activity, specifying the number of days
        in the past from the current date to return.

        If a survey_id is specified, only activity from that
        survey will be returned.
        """
        user = self.current_user_model
        if user is None:
            raise exc.Unauthorized()

        # number of days prior to return
        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=days - 1)

        # truncate the datetime to just the day
        date_trunc = func.date_trunc('day', Submission.submission_time)

        query = self.session.query(
            date_trunc, func.count()).filter(
            User.id == user.id).filter(
            Submission.submission_time >= from_date)

        if survey_id is not None:
            query = query.filter(Submission.survey_id == survey_id)

        query = query.group_by(
            date_trunc)

        result = query.order_by(date_trunc.desc()).all()

        response = {
            'activity': []
        }
        for day in result:
            response['activity'].append({
                'date': day[0],
                'num_submissions': day[1]
            })
        return response

        def prepare(self, data):
            """
            If we don't prep the data, all the fields get returned!

            We can subtract fields here if there are fields which shouldn't
            be included in the API.
            """
            return data
