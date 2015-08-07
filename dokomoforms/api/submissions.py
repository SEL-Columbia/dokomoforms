"""TornadoResource class for dokomoforms.models.submission.Submission."""
import restless.exceptions as exc

from sqlalchemy.orm.exc import NoResultFound

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer, Answer,
    SurveyNode, skipped_required,
    get_model
)
from dokomoforms.models.answer import ANSWER_TYPES
from dokomoforms.exc import RequiredQuestionSkipped


def _create_answer(session, answer_dict) -> Answer:
    try:
        survey_node_id = answer_dict['survey_node_id']
        survey_node = get_model(session, SurveyNode, survey_node_id)
    except NoResultFound:
        raise exc.BadRequest(
            'survey_node not found: {}'.format(survey_node_id)
        )
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
            enumerator = self.get_model(
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

        # pass submission props as kwargs
        if 'submission_type' not in self.data:
            # by default fall to authenticated (i.e. EnumOnlySubmission)
            self.data['submission_type'] = 'authenticated'

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

    def is_authenticated(self):
        """Allow unauthenticated POSTs under the right circumstances."""
        if self.request_method() == 'POST':
            # At this point in the lifecycle of the request, self.data has
            # not been populated, so we need to handle POST authentication
            # in the create method.
            return True
        return super().is_authenticated()

    # POST /api/submissions/
    def create(self):
        """Create a new submission.

        Uses the current_user_model (i.e. logged-in user) as creator.
        """
        survey_id = self.data.pop('survey_id')
        try:
            survey = self.get_model(survey_id, model_cls=Survey)
        except NoResultFound:
            raise exc.BadRequest(
                'The survey could not be found: {}'.format(survey_id)
            )
        return _create_submission(self, survey)


def get_submission_for_handler(tornado_handler, submission_id):
    """Maybe a handler needs a submission from the API."""
    submission_resource = SubmissionResource()
    submission_resource.ref_rh = tornado_handler
    submission_resource.request = tornado_handler.request
    submission_resource.application = tornado_handler.application
    return submission_resource.detail(submission_id)
