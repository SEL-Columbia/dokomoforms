import tornado.web

from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import Submission, construct_submission_node


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
        'title': 'title',
        'default_language': 'default_language',
        'translations': 'translations',
        'enumerator_only': 'enumerator_only',
        'version': 'version',
        'creator_id': 'creator_id',
        'creator_name': 'creator.name',
        'metadata': 'submission_metadata',
        'created_on': 'created_on',
        'last_update_time': 'last_update_time',
        'nodes': 'nodes',
    })

    # GET /api/submissions/
    def list(self):
        submissions = self.session.query(Submission).filter(
            Submission.deleted is not False).all()
        return submissions

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
        if self.current_user_model is None:
            raise tornado.web.HTTPError(
                403,
                reason=(
                    'You do not have sufficient privilages.'
                ),
            )

        def create_submission_node(node):
            # pass node props as kwargs
            print(node)
            return construct_submission_node(**node)

        with self.session.begin():
            # create a list of Node models
            nodes = list(map(create_submission_node, self.data['nodes']))
            # remove the existing nodes key from the received data
            del self.data['nodes']
            creator = self.current_user_model
            # pass submission props as kwargs
            submission = Submission(**self.data)
            # add the node models
            submission.nodes = nodes
            # add the submission to the creator
            creator.submissions.append(submission)

        return submission

    # PUT /api/submissions/<submission_id>/
    def update(self, submission_id):
        submission = self.session.query(Submission).get(submission_id)
        if not submission:
            raise exc.NotFound()
        else:
            return submission

    # DELETE /api/submissions/<submission_id>/
    def delete(self, submission_id):
        """
        curl -X DELETE -H "Content-Type: application/json"
        http://local.dokomoforms.org:8888/api/v0/submissions/e383f48c-674f-4ab9-a919-bbf1ca7bfb46
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
