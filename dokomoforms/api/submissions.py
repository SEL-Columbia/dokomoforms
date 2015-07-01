from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer,
    SurveyNode
)


class SubmissionResource(BaseResource):
    """
    Restless resource for Submissions.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'submissions'

    # The preparer defines the fields that get returned.
    preparer = FieldsPreparer(fields={
        'id': 'id',
        'deleted': 'deleted',
        'survey_id': 'survey_id',
        'save_time': 'save_time',
        'submission_time': 'submission_time',
        'last_update_time': 'last_update_time',
        'submitter_name': 'submitter_name',
        'submitter_email': 'submitter_email',
        'answers': 'answers',
    })

    # GET /api/submissions/
    def list(self):
        response = self._generate_list_response(Submission)
        return response

    # GET /api/submissions/<submission_id>
    def detail(self, submission_id):
        submission = self.session.query(Submission).get(submission_id)
        if not submission:
            raise exc.NotFound()
        return submission

    # POST /api/submissions/
    def create(self):
        """
        Creates a new submission using the current_user_model
        (i.e. logged-in user) as creator.
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

        # If an enumerator ID is present, add the enumerator
        if 'enumerator_user_id' in self.data:
            enumerator = self.session.query(
                User).get(self.data['enumerator_user_id'])
            self.data['enumerator'] = enumerator

        self.data['survey'] = survey

        def create_answer(answer_dict):
            # put the survey_node model in place of the survey_node_id
            if 'survey_node_id' in answer_dict:
                survey_node = self.session.query(SurveyNode).get(
                    answer_dict['survey_node_id'])
                if survey_node is not None:
                    answer_dict['survey_node'] = survey_node
                    return construct_answer(**answer_dict)

        with self.session.begin():
            # create a list of Answer models
            if 'answers' in self.data:
                answers = list(map(create_answer, self.data['answers']))
                self.data['answers'] = answers
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
        """
        Marks the submission.deleted = True. Does NOT remove the submission
        from the DB.
        """
        with self.session.begin():
            submission = self.session.query(Submission).get(submission_id)
            if not submission:
                raise exc.NotFound()
            submission.deleted = True
