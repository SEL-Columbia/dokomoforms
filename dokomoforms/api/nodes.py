from restless.preparers import FieldsPreparer
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Node, Choice, construct_node
)


class NodeResource(BaseResource):
    """
    Restless resource for Nodes.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'nodes'

    # GET /api/nodes/
    def list(self):
        """Return a list of nodes."""
        response = self._generate_list_response(Node)
        return response

    # GET /api/nodes/<node_id>
    def detail(self, node_id):
        """Return a single node."""
        node = self.session.query(Node).get(node_id)
        if node is None:
            raise exc.NotFound()
        else:
            return node

    # POST /api/nodes/
    def create(self):
        """
        Create a new node.
        """

        def create_choice(choice):
            return Choice(**choice)

        with self.session.begin():
            # create a list of Node models
            # - if the node is a multiple_choice, create Choice models
            # first creating the node.
            if self.data['type_constraint'] == 'multiple_choice':
                if 'choices' in self.data:
                    choices = list(map(create_choice, self.data['choices']))
                    self.data['choices'] = choices

            node = construct_node(**self.data)
            self.session.add(node)

        return node

    # PUT /api/nodes/<node_id>/
    def update(self, node_id):
        """TODO: how should this behave?"""
        node = self.session.query(Node).get(node_id)

        if node is None:
            raise exc.NotFound()
        else:
            with self.session.begin():
                node.update(self.data)
            return node

    # DELETE /api/nodes/<node_id>/
    def delete(self, node_id):
        """
        Marks the node.deleted = True. Does NOT remove the node
        from the DB.
        """
        with self.session.begin():
            node = self.session.query(Node).get(node_id)
            if node is None:
                raise exc.NotFound()
            else:
                node.deleted = True

    def prepare(self, data):
        """
        If we don't prep the data, all the fields get returned!

        We can subtract fields here if there are fields which shouldn't
        be included in the API.
        """
        return data
