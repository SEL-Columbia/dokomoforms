from restless.tnd import TornadoResource

from sqlalchemy.sql.expression import false

from dokomoforms.api.serializer import ModelJSONSerializer
from dokomoforms.handlers.util import BaseAPIHandler

"""
A list of the expected query arguments
"""
QUERY_ARGS = [
    'limit',
    'offset',
    'type',
    'draw'
]


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

    @property
    def current_user(self):
        return self.r_handler.current_user

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
        response = {
            self.objects_key: data
        }
        # add additional properties to the response object
        full_response = self._add_meta_props(response)

        return full_response

    def is_authenticated(self):
        if self.request_method() == 'GET':
            return True

        # Require logged-in user to POST/PUT/DELETE
        return self.r_handler.current_user is not None

        # Alternatively, you could check an API key. (Need a model for this...)
        # from myapp.models import ApiKey
        # try:
        #     key = ApiKey.objects.get(key=self.request.GET.get('api_key'))
        #     return True
        # except ApiKey.DoesNotExist:
        #     return False

    def _generate_list_response(self, model_cls, **kwargs):
        """
        Given a model class, build up the ORM query based on query params
        and return the query result.
        """
        query = self.session.query(model_cls)

        limit = self.r_handler.get_query_argument('limit', None)
        offset = self.r_handler.get_query_argument('offset', None)
        deleted = self.r_handler.get_query_argument('show_deleted', 'false')
        search_term = self.r_handler.get_query_argument('search', None)
        search_fields = self.r_handler.get_query_argument(
            'search_fields', 'title')
        # TODO: this
        # search_lang = self.r_handler.get_query_argument('lang', 'English')
        type = self.r_handler.get_query_argument('type', None)

        if deleted.lower() != 'true':
            query = query.filter(model_cls.deleted == false())

        if type is not None:
            query = query.filter(model_cls.type_constraint == type)

        if limit is not None:
            query = query.limit(int(limit))

        if offset is not None:
            query = query.offset(int(offset))

        # TODO: this isn't complete -- needs jsonb lookupability.
        if search_term is not None:
            search_fields_list = search_fields.split(',')
            for search_field in search_fields_list:
                if hasattr(model_cls, search_field):
                    query = query.filter(
                        getattr(
                            model_cls, search_field
                        ).ilike('%' + search_term + '%'))

        return query.all()

    def _add_meta_props(self, response):
        """
        Add the appropriate metadata fields to the response body object. Any
        properties that should sit alongside the list of objects being
        returned should be added here.

        e.g. if the request contained a limit, include the limit value in
        the response:

        {
            "objects": [{
                "title": "Testing"
            },
            {
                "title": "Check One"
            }],
            "limit": 5
        }

        TODO: this will require a bit more sophistication, since we probably
        don't want to just reflect query params willy nilly.
        """
        for prop in QUERY_ARGS:
            prop_value = self.r_handler.get_query_argument(prop, None)
            if prop_value is not None:
                if prop_value.isdigit():
                    prop_value = int(prop_value)
                response[prop] = prop_value

        return response
