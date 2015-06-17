from restless.tnd import TornadoResource
from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import Survey


class SurveyResource(BaseResource):

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
        'metadata': 'metadata',
        'created_on': 'created_on',
        'last_update_time': 'last_update_time',
        'nodes': 'nodes',
    })

    # GET /api/surveys/
    def list(self):
        return self.session.query(Survey).all()

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
        curl -X POST -H "Content-Type: application/json" \
            -d '{"title": "New Test Survey"}' \
            http://local.dokomoforms.org:8888/api/surveys
        """
        with self.session.begin():
            survey = Survey(
                title=self.data['title'],
                enumerator_only='false',
                creator_id='756d7705-c4ea-434d-98f8-4382532f5a3f'
            )

            self.session.add(survey)
            self.session.commit()

            """
            creator = models.SurveyCreator(
                name='creator',
                emails=[models.Email(address='email')],
            )
            node_types = list(models.NODE_TYPES)
            for node_type in node_types:
                survey = models.Survey(
                    title=node_type + '_survey',
                    nodes=[
                        models.SurveyNode(
                            node=models.construct_node(
                                type_constraint=node_type,
                                title=node_type + '_node',
                            ),
                        ),
                    ],
                )
                creator.surveys.append(survey)
            self.session.add(creator)
            """
        return survey

    # Add this!
    # PUT /api/surveys/<survey_id>/
    def update(self, survey_id):
        pass

    # Add this!
    # DELETE /api/surveys/<survey_id>/
    def delete(self, survey_id):
        survey = self.session.query(Survey).get(survey_id)
        if not survey:
            raise exc.NotFound()
        else:
            survey.deleted = True
            self.session.commit()
