"""TornadoResource class for dokomoforms.models.submission.Submission."""

import restless.exceptions as exc

from dokomoforms.handlers.api.v0 import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer, Answer,
    SurveyNode, skipped_required,
    get_model
)
from dokomoforms.models.answer import ANSWER_TYPES
from dokomoforms.exc import RequiredQuestionSkipped


def _create_answer(session, answer_dict) -> Answer:
    survey_node_id = answer_dict['survey_node_id']
    error = exc.BadRequest('survey_node not found: {}'.format(survey_node_id))
    survey_node = get_model(session, SurveyNode, survey_node_id, error)
    answer_dict['survey_node'] = survey_node
    return construct_answer(**answer_dict)


def _create_submission(self, survey):
    # Unauthenticated submissions are only allowed if the survey_type is
    # 'public'.
    authenticated = super(self.__class__, self).is_authenticated()
    if not authenticated:
        if survey.survey_type == 'public':
            self._check_xsrf_cookie()
        else:
            raise exc.Unauthorized()

    # If logged in, add enumerator
    if self.current_user_model is not None:
        try:
            enumerator = self._get_model(
                self.data['enumerator_user_id'], model_cls=User
            )
        except KeyError:
            self.data['enumerator'] = self.current_user_model
        else:
            self.data['enumerator'] = enumerator

    self.data['survey'] = survey

    with self.session.begin():
        # create a list of Answer models
        if 'answers' in self.data:
            raw_answers = self.data['answers']
            answers = [
                _create_answer(self.session, answer) for answer in raw_answers
            ]
            self.data['answers'] = answers

        self.data['submission_type'] = survey.survey_type + '_submission'

        submission = construct_submission(**self.data)

        # add the answer models
        # if 'answers' in self.data:
        #    submission.answers = answers

        # add the submission
        self.session.add(submission)
        self.session.flush()

        for answer in submission.answers:
            answer.main_answer = (
                self.session
                .query(ANSWER_TYPES[answer.answer_type].main_answer)
                .filter_by(id=answer.id)
                .scalar()
            )

        skipped_question = skipped_required(survey, submission.answers)
        if skipped_question is not None:
            raise RequiredQuestionSkipped(
                '{} skipped'.format(skipped_question)
            )

    return submission


class SubmissionResource(BaseResource):

    """Restless resource for Submissions.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    resource_type = Submission
    default_sort_column_name = 'save_time'
    objects_key = 'submissions'
    fieldnames = [
        'id', 'deleted', 'answer_number', 'submission_id', 'save_time',
        'survey_id', 'survey_node_id', 'question_id', 'type_constraint',
        'last_update_time', 'main_answer', 'response', 'response_type',
        'metadata'
    ]
    survey_id = None

    def wrap_list_response(self, data):
        """Allow CSV export of submission data.

        This method adds CSV export functionality on top of the JSON list
        wrapping of BaseResource.wrap_list_response.
        """
        if self.content_type == 'csv':
            if 'Content-Disposition' not in self.ref_rh._headers.keys():
                self._set_filename('submissions', 'csv')
            dialect = self._query_arg('dialect', default='excel')
            return {
                'format': 'csv',
                'fieldnames': self.fieldnames,
                'dialect': dialect,
                'data': data[2],
            }
        if self.survey_id is None:
            return super().wrap_list_response(data)
        else:
            return super().wrap_list_response(data, survey_id=self.survey_id)

    def is_authenticated(self):
        """Allow unauthenticated POSTs under the right circumstances."""
        if self.request_method() == 'POST':
            # At this point in the lifecycle of the request, self.data has
            # not been populated, so we need to handle POST authentication
            # in the create method.
            return True
        return super().is_authenticated()

    def detail(self, submission_id):
        """Allow CSV export of a single submission."""
        if self.content_type == 'csv':
            self._set_filename('submission_{}'.format(submission_id), 'csv')
            dialect = self._query_arg('dialect', default='excel')
            return {
                'format': 'csv',
                'fieldnames': self.fieldnames,
                'dialect': dialect,
                'data': [self._get_model(submission_id)],
            }
        return super().detail(submission_id)

    def list(self, survey_id=None):
        """List submissions, and restrict to a survey if the id is given."""
        where = None
        if survey_id is not None:
            self.survey_id = survey_id
            where = Submission.survey_id == survey_id
            if self.content_type == 'csv':
                title = (
                    self.session
                    .query(Survey.title[Survey.default_language])
                    .filter_by(id=survey_id)
                    .scalar()
                )
                self._set_filename(
                    'survey_{}_submissions'.format(title), 'csv')
        return super().list(where=where)

    # POST /api/submissions/
    def create(self):
        """Create a new submission.

        Uses the current_user_model (i.e. logged-in user) as creator.
        """
        survey_id = self.data.pop('survey_id')
        error = exc.BadRequest(
            'The survey could not be found: {}'.format(survey_id)
        )
        survey = self._get_model(survey_id, model_cls=Survey, exception=error)
        return _create_submission(self, survey)


def get_submission_for_handler(tornado_handler, submission_id):
    """Maybe a handler needs a submission from the API."""
    submission_resource = SubmissionResource()
    submission_resource.ref_rh = tornado_handler
    submission_resource.request = tornado_handler.request
    submission_resource.application = tornado_handler.application
    return submission_resource.detail(submission_id)
