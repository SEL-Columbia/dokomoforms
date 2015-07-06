"""TornadoResource class for dokomoforms.models.submission.Submission."""
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer, Answer,
    SurveyNode
)


def _create_answer(session, answer_dict) -> Answer:
    survey_node = (
        session
        .query(SurveyNode)
        .get(answer_dict['survey_node_id'])
    )
    if survey_node is not None:
        answer_dict['survey_node'] = survey_node
        return construct_answer(**answer_dict)
    # TODO: Raise an exception


class SubmissionResource(BaseResource):

    """Restless resource for Submissions.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'submissions'

    # GET /api/submissions/
    def list(self):
        """Return a list of submissions."""
        response = self._generate_list_response(Submission)
        return response

    # GET /api/submissions/<submission_id>
    def detail(self, submission_id):
        """Return a single submission."""
        submission = self.session.query(Submission).get(submission_id)
        if not submission:
            raise exc.NotFound()
        return submission

    # POST /api/submissions/
    def create(self):
        """Create a new submission.

        Uses the current_user_model (i.e. logged-in user) as creator.
        """
        if 'survey_id' not in self.data:
            raise exc.BadRequest(
                "'survey_id' property is required."
            )

        survey = self.session.query(Survey).get(self.data['survey_id'])

        if survey is None:
            raise exc.BadRequest(
                "The survey could not be found."
            )

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

    # PUT /api/submissions/<submission_id>/
    def update(self, submission_id):
        """TODO: Update a submission."""
        submission = self.session.query(Submission).get(submission_id)
        if not submission:
            raise exc.NotFound()
        # TODO: FIX THIS
        else:
            # with self.session.begin():
                # submission.update(self.data)
            return submission

    # DELETE /api/submissions/<submission_id>/
    def delete(self, submission_id):
        """Set submission.deleted = True.

        Does NOT remove the submission from the DB.
        """
        with self.session.begin():
            submission = self.session.query(Submission).get(submission_id)
            if not submission:
                raise exc.NotFound()
            submission.deleted = True
