"""TornadoResource class for dokomoforms.models.node.Node subclasses."""
from dokomoforms.handlers.api.v0 import BaseResource
from dokomoforms.models import (
    Node, Choice, construct_node
)


class NodeResource(BaseResource):

    """Restless resource for Nodes.

    BaseResource sets the serializer, which uses the dokomo models'
    ModelJSONEncoder for json conversion.
    """

    resource_type = Node
    default_sort_column_name = 'last_update_time'
    objects_key = 'nodes'

    def create(self):
        """Create a new node."""
        is_mc = self.data['type_constraint'] == 'multiple_choice'
        with self.session.begin():
            # create a list of Node models
            # - if the node is a multiple_choice, create Choice models
            # first creating the node.
            if is_mc and 'choices' in self.data:
                self.data['choices'] = [
                    Choice(**choice) for choice in self.data['choices']
                ]

            node = construct_node(**self.data)
            self.session.add(node)

        return node

    # def prepare(self, data):
    #     """Determine which fields to return.

    #     If we don't prep the data, all the fields get returned!

    #     We can subtract fields here if there are fields which shouldn't
    #     be included in the API.
    #     """
    #     return data
