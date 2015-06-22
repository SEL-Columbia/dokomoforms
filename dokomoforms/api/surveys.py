import tornado.web

from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import Survey, construct_survey_node


class SurveyResource(BaseResource):
    """
    Restless resource for Surveys.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'surveys'

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
        'metadata': 'survey_metadata',
        'created_on': 'created_on',
        'last_update_time': 'last_update_time',
        'nodes': 'nodes',
    })

    # GET /api/surveys/
    def list(self):
        surveys = self.session.query(Survey).filter(
            Survey.deleted is not False).all()
        return surveys

    # GET /api/surveys/<survey_id>
    def detail(self, survey_id):
        survey = self.session.query(Survey).get(survey_id)
        if not survey:
            raise exc.NotFound()
        else:
            return survey

    # POST /api/surveys/
    def create(self):
        """
        Creates a new survey using the current_user_model (i.e. logged-in user)
        as creator.
        """
        if self.current_user_model is None:
            raise tornado.web.HTTPError(
                403,
                reason=(
                    'You do not have sufficient privilages.'
                ),
            )

        def create_survey_node(node):
            # pass node props as kwargs
            print(node)
            return construct_survey_node(**node)

        with self.session.begin():
            # create a list of Node models
            nodes = list(map(create_survey_node, self.data['nodes']))
            del self.data['nodes']
            # pass survey props as kwargs
            creator = self.current_user_model
            survey = Survey(**self.data)
            survey.nodes = nodes
            creator.surveys.append(survey)

        return survey

    # PUT /api/surveys/<survey_id>/
    def update(self, survey_id):
        survey = self.session.query(Survey).get(survey_id)
        if not survey:
            raise exc.NotFound()
        else:
            return survey

    # DELETE /api/surveys/<survey_id>/
    def delete(self, survey_id):
        """
        curl -X DELETE -H "Content-Type: application/json"
        http://local.dokomoforms.org:8888/api/v0/surveys/e383f48c-674f-4ab9-a919-bbf1ca7bfb46
        """
        with self.session.begin():
            survey = self.session.query(Survey).get(survey_id)
            if not survey:
                raise exc.NotFound()
            else:
                survey.deleted = True

    def prepare(self, data):
        # ``data`` is the object/dict to be exposed.
        # We'll call ``super`` to prep the data, then we can modify it.
        prepped = super().prepare(data)

        # modify prepped here

        # then return the modified data.
        return prepped
