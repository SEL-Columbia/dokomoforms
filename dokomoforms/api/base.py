"""The base class of the TornadoResource classes in the api module."""
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from time import localtime

from passlib.hash import bcrypt_sha256

from restless.tnd import TornadoResource
import restless.exceptions as exc

from sqlalchemy import text, func
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.functions import count
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

import tornado.web

from dokomoforms.api.serializer import ModelJSONSerializer
from dokomoforms.handlers.util import BaseHandler, BaseAPIHandler
from dokomoforms.models import SurveyCreator, Email
from dokomoforms.models.util import column_search, get_fields_subset
from dokomoforms.exc import DokomoError

# TODO: Find out if it is OK to remove these. @jmwohl
# """
# A list of the expected query arguments
# """
# QUERY_ARGS = [
#     'limit',
#     'offset',
#     'type',
#     'draw',
#     'fields',
# ]


class BaseResource(TornadoResource, metaclass=ABCMeta):

    """Set up the basics for the model resource.

    BaseResource does some basic configuration for the restless resources.
    - sets the base request handler class which is used by the resources
    - providing reference to the ORM session via request handler
    - inserting a serializer for dokomo Models
    - setting up authentication
    """

    _request_handler_base_ = BaseAPIHandler

    # The serializer is used to serialize / deserialize models to json
    serializer = ModelJSONSerializer()

    @property  # pragma: no cover
    @abstractmethod
    def resource_type(self):
        """The model class for the resource."""

    @property  # pragma: no cover
    @abstractmethod
    def default_sort_column_name(self):
        """The default ORDER BY column name for list responses."""

    @property  # pragma: no cover
    @abstractmethod
    def objects_key(self):
        """The key for list responses."""

    @property
    def session(self):
        """The handler's session."""
        return self.r_handler.session

    @property
    def current_user_model(self):
        """The handler's current_user_model."""
        return self.r_handler.current_user_model

    @property
    def current_user(self):
        """The handler's current_user."""
        return self.r_handler.current_user

    def _query_arg(self, argument_name, output=None, default=None):
        """Get a useful query parameter argument."""
        arg = self.r_handler.get_query_argument(argument_name, None)

        # Return default if the argument was not given.
        if not arg:
            return default

        # Convert 'true'/'false' argument into True or False
        if output is bool:
            return arg.lower() == 'true'

        # Convert a comma-separated list to a list of strings
        if output is list:
            return arg.split(',')

        # Apply the parsing function if supplied.
        if output is not None:
            return output(arg)

        return arg

    def handle_error(self, err):
        """Generate a serialized error message.

        If the error came from Tornado, pass it along as such.
        Otherwise, turn certain expected errors into 400 BAD REQUEST instead
        of 500 INTERNAL SERVER ERROR.
        """
        understood = (
            KeyError, ValueError, TypeError, AttributeError,
            SQLAlchemyError, DokomoError
        )

        if isinstance(err, tornado.web.HTTPError):
            restless_error = exc.HttpError(err.log_message)
            restless_error.status = err.status_code
            err = restless_error
        elif isinstance(err, understood):
            err = exc.BadRequest(err)
        return super().handle_error(err)

    def wrap_list_response(self, data):
        """Wrap a list response in a dict.

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
        response = OrderedDict((
            (self.objects_key, data[1]),
            (
                'total_entries',
                self.session.query(func.count(self.resource_type.id)).scalar()
            ),
            ('filtered_entries', data[0]),
        ))
        # add additional properties to the response object
        full_response = self._add_meta_props(response)

        return full_response

    def _check_xsrf_cookie(self):
        return BaseHandler.check_xsrf_cookie(self.r_handler)

    def is_authenticated(self):
        """Return whether the request has been authenticated."""
        # A logged-in user has already authenticated.
        if self.r_handler.current_user is not None:
            self._check_xsrf_cookie()
            return True

        # A SurveyCreator can log in with a token.
        token = self.r_handler.request.headers.get('Token', None)
        email = self.r_handler.request.headers.get('Email', None)
        if (token is not None) and (email is not None):
            # Get the user's token hash and expiration time.
            try:
                user = (
                    self.session
                    .query(SurveyCreator.token, SurveyCreator.token_expiration)
                    .join(Email)
                    .filter(Email.address == email)
                    .one()
                )
            except NoResultFound:
                return False
            # Check that the token has not expired
            if user.token_expiration.timetuple() < localtime():
                return False
            # Check the token
            token_exists = user.token is not None
            return token_exists and bcrypt_sha256.verify(token, user.token)

        return False

    def _specific_fields(self, model_or_models, is_detail=True):
        """Pick out the specified fields on the given models.

        TODO: Confirm that this is not a performance bottleneck.
        """
        fields = self._query_arg('fields', list)

        # No fields specified -> return them all.
        if fields is None:
            return model_or_models

        if is_detail:
            the_model = model_or_models
            return get_fields_subset(the_model, fields)
        models = model_or_models
        return [get_fields_subset(model, fields) for model in models]

    def detail(self, model_id):
        """Return a single instance of a model."""
        model = self.session.query(self.resource_type).get(model_id)
        if model is None:
            raise exc.NotFound()
        return self._specific_fields(model)

    def list(self, where=None):
        """Return a list of instances of this model.

        Given a model class, build up the ORM query based on query params
        and return the query result.
        """
        model_cls = self.resource_type
        query = self.session.query(model_cls, count().over())

        limit = self._query_arg('limit', int)
        offset = self._query_arg('offset', int)
        deleted = self._query_arg('show_deleted', bool, False)
        search_term = self._query_arg('search')
        regex = self._query_arg('regex', bool, False)
        search_fields = self._query_arg(
            'search_fields', list, default=['title']
        )
        search_lang = self._query_arg('lang')

        default_sort = ['{}:DESC'.format(self.default_sort_column_name)]
        order_by_text = (
            element.split(':') for element in self._query_arg(
                'order_by', list, default=default_sort
            )
        )

        type_constraint = self._query_arg('type')

        if search_term is not None:
            for search_field in search_fields:
                query = column_search(
                    query,
                    model_cls=model_cls,
                    column_name=search_field,
                    search_term=search_term,
                    language=search_lang,
                    regex=regex,
                )

        if not deleted:
            query = query.filter(model_cls.deleted == false())

        if type_constraint is not None:
            query = query.filter(model_cls.type_constraint == type_constraint)

        if where is not None:
            query = query.filter(where)

        for attribute_name, direction in order_by_text:
            try:
                order = getattr(model_cls, attribute_name)
                direction = direction.lower()
                if direction == 'asc':
                    order = order.asc()
                elif direction == 'desc':
                    order = order.desc()
                order = order.nullslast()
            except AttributeError:
                order = text(
                    '{} {} NULLS LAST'.format(attribute_name, direction)
                )
            query = query.order_by(order)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        result = query.all()
        if result:
            num_filtered = result[0][1]
            models = [res[0] for res in result]
            return num_filtered, self._specific_fields(models, is_detail=False)
        return 0, []

    def update(self, model_id):
        """Update a model."""
        model = self.session.query(self.resource_type).get(model_id)

        if model is None:
            raise exc.NotFound()

        with self.session.begin():
            for attribute, value in self.data.items():
                setattr(model, attribute, value)
            self.session.add(model)
        return model

    def delete(self, model_id):
        """Set the deleted attribute to True. Does not destroy the instance."""
        with self.session.begin():
            model = self.session.query(self.resource_type).get(model_id)
            if model is None:
                raise exc.NotFound()
            model.deleted = True

    def _add_meta_props(self, response):
        """Add metadata to the response.

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
        for prop in sorted(self.r_handler.request.arguments):
            prop_value = self.r_handler.get_query_argument(prop)
            if prop_value.isdigit():
                prop_value = int(prop_value)
            response[prop] = prop_value

        return response
