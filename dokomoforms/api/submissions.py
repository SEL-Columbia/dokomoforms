from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Survey, Submission, User,
    construct_submission, construct_answer
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
        else:
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

    # PUT /api/submissions/<submission_id>/
    def update(self, submission_id):
        submission = self.session.query(Submission).get(submission_id)
        if not submission:
            raise exc.NotFound()
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
            else:
                submission.deleted = True

    def prepare(self, data):
        # ``data`` is the object/dict to be exposed.
        # We'll call ``super`` to prep the data, then we can modify it.
        prepped = super().prepare(data)

        # modify prepped here

        # then return the modified data.
        return prepped
