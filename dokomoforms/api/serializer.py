"""The restless Serializer for the models."""
from restless.serializers import Serializer
from dokomoforms.models import ModelJSONEncoder
import json


class ModelJSONSerializer(Serializer):

    """Drop-in replacement for the restless-supplied JSONSerializer.

    Uses dokomo's ModelJSONEncoder in order to correctly serialize models
    to JSON.
    """

    def deserialize(self, body):
        """The low-level deserialization.

        Underpins ``deserialize``, ``deserialize_list`` &
        ``deserialize_detail``.
        Has no built-in smarts, simply loads the JSON.
        :param body: The body of the current request
        :type body: string
        :returns: The deserialized data
        :rtype: ``list`` or ``dict``
        """
        if isinstance(body, bytes):
            return json.loads(body.decode('utf-8'))
        return json.loads(body)

    def serialize(self, data):
        """The low-level serialization.

        Underpins ``serialize``, ``serialize_list`` &
        ``serialize_detail``.
        Has no built-in smarts, simply dumps the JSON.
        :param data: The body for the response
        :type data: string
        :returns: A serialized version of the data
        :rtype: string
        """
        return json.dumps(data, cls=ModelJSONEncoder).replace('</', '<\\/')
