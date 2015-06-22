from restless.tnd import TornadoResource

from dokomoforms.api.serializer import ModelJSONSerializer
from dokomoforms.handlers.util import BaseAPIHandler


class BaseResource(TornadoResource):
    """
    BaseResource does some basic configuration for the restless resources.
    - sets the base request handler class which is used by the resources
    - providing reference to the ORM session via request handler
    - inserting a serializer for dokomo Models
    - setting up authentication
    """

    _request_handler_base_ = BaseAPIHandler

    # The serializer is used to serialize / deserialize models to json
    serializer = ModelJSONSerializer()

    # The name of the property for the array of objects returned in a json list
    objects_key = 'objects'

    @property
    def session(self):
        return self.r_handler.session

    @property
    def current_user_model(self):
        return self.r_handler.current_user_model

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
            self.objects_key: data
        }

    def is_authenticated(self):
        # Open everything wide!
        # DANGEROUS, DO NOT DO IN PRODUCTION.
        return True

        # Alternatively, if the user is logged into the site...
        # return self.request.user.is_authenticated()

        # Alternatively, you could check an API key. (Need a model for this...)
        # from myapp.models import ApiKey
        # try:
        #     key = ApiKey.objects.get(key=self.request.GET.get('api_key'))
        #     return True
        # except ApiKey.DoesNotExist:
        #     return False
