"""TornadoResource class for dokomoforms.models.node.Node subclasses."""
import restless.exceptions as exc

from dokomoforms.api import BaseResource
from dokomoforms.models import (
    Node, Choice, construct_node
)


class NodeResource(BaseResource):

    """Restless resource for Nodes.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    # Set the property name on the outputted json
    objects_key = 'nodes'

    def list(self):
        """Return a list of nodes."""
        response = self._generate_list_response(Node)
        return response

    def detail(self, node_id):
        """Return a single node."""
        node = self.session.query(Node).get(node_id)
        if node is None:
            raise exc.NotFound()
        return node

    def create(self):
        """Create a new node."""
        with self.session.begin():
            # create a list of Node models
            # - if the node is a multiple_choice, create Choice models
            # first creating the node.
            is_mc = self.data['type_constraint'] == 'multiple_choice'
            if is_mc and 'choices' in self.data:
                self.data['choices'] = [
                    Choice(**choice) for choice in self.data['choices']
                ]

            node = construct_node(**self.data)
            self.session.add(node)

        return node

    def update(self, node_id):
        """TODO: how should this behave? Good question."""
        return self._update(Node, node_id)

    def delete(self, node_id):
        """Set node.deleted = True.

        Does NOT remove the node from the DB.
        """
        with self.session.begin():
            node = self.session.query(Node).get(node_id)
            if node is None:
                raise exc.NotFound()
            node.deleted = True

    def prepare(self, data):
        """Determine which fields to return.

        If we don't prep the data, all the fields get returned!

        We can subtract fields here if there are fields which shouldn't
        be included in the API.
        """
        return data
