from restless.tnd import TornadoResource
from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import Survey


class SurveyResource(BaseResource):
    """
    Restless resource for Surveys.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

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
        surveys = self.session.query(Survey).all()
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

    def wrap_list_response(self, data):
        """
        Takes a list of data & wraps it in a dictionary (within the ``objects``
        key).
        For security in JSON responses, it's better to wrap the list results in
        an ``object`` (due to the way the ``Array`` constructor can be attacked
        in Javascript).
        See http://haacked.com/archive/2009/06/25/json-hijacking.aspx/
        & similar for details.
        Overridable to allow for modifying the key names, adding data (or just
        insecurely return a plain old list if that's your thing).
        :param data: A list of data about to be serialized
        :type data: list
        :returns: A wrapping dict
        :rtype: dict
        """
        return {
            "surveys": data
        }

    def prepare(self, data):
        # ``data`` is the object/dict to be exposed.
        # We'll call ``super`` to prep the data, then we'll mask the email.
        prepped = super().prepare(data)

        # nodes = prepped['nodes']
        # prepped['email'] = email[:at_offset + 1] + "..."

        return prepped
