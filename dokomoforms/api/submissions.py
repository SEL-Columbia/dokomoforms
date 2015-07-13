"""TornadoResource class for dokomoforms.models.submission.Submission."""
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer, Answer,
    SurveyNode
)


def _create_answer(session, answer_dict) -> Answer:
    survey_node_id = answer_dict.get('survey_node_id', None)
    if survey_node_id is None:
        raise exc.BadRequest("'survey_node_id' property is required.")
    survey_node = (
        session
        .query(SurveyNode)
        .get(survey_node_id)
    )
    if survey_node is not None:
        answer_dict['survey_node'] = survey_node
        return construct_answer(**answer_dict)
    raise exc.BadRequest('survey_node not found: {}'.format(survey_node_id))


def _create_submission(self, survey):
    # Unauthenticated submissions are only allowed if the survey_type is
    # 'public'.
    authenticated = super(self.__class__, self).is_authenticated()
    if not authenticated and survey.survey_type != 'public':
        raise exc.Unauthorized()

    # If logged in, add enumerator
    if self.current_user_model is not None:
        if 'enumerator_user_id' in self.data:
            # if enumerator_user_id is provided, use that user
            enumerator = self.session.query(
                User).get(self.data['enumerator_user_id'])
            self.data['enumerator'] = enumerator
        else:
            # otherwise the currently logged in user
            self.data['enumerator'] = self.current_user_model

    self.data['survey'] = survey

    with self.session.begin():
        # create a list of Answer models
        if 'answers' in self.data:
            answers = self.data['answers']
            self.data['answers'] = [
                _create_answer(self.session, answer) for answer in answers
            ]
            # del self.data['answers']

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
        survey_id = self.data.pop('survey_id', None)
        if survey_id is None:
            raise exc.BadRequest(
                "'survey_id' property is required."
            )
        survey = self.session.query(Survey).get(survey_id)
        if survey is None:
            raise exc.BadRequest(
                'The survey could not be found: {}'.format(survey_id)
            )
        return _create_submission(self, survey)
