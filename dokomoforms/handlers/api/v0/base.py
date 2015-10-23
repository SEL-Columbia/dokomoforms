"""The base class of the TornadoResource classes in the api module."""
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import datetime
from time import localtime

from passlib.hash import bcrypt_sha256

from restless.tnd import TornadoResource
import restless.exceptions as exc

from sqlalchemy import text, func
from sqlalchemy.sql.functions import count
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

import tornado.web

from dokomoforms.handlers.api.v0.serializer import ModelJSONSerializer
from dokomoforms.handlers.api.v0.util import filename_safe
from dokomoforms.handlers.util import BaseHandler, BaseAPIHandler
from dokomoforms.models import Administrator, Email, Survey, Submission
from dokomoforms.models.survey import (
    administrator_filter, _administrator_table
)
from dokomoforms.models.util import column_search, get_fields_subset, get_model
from dokomoforms.exc import DokomoError


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
        logged_in_user = self.r_handler.current_user_model
        if logged_in_user:
            return logged_in_user
        try:
            email = self.r_handler.request.headers['Email']
        except KeyError:
            return None
        try:
            return (
                self.session
                .query(Administrator)
                .join(Email)
                .filter(Email.address == email)
                .one()
            )
        except NoResultFound:
            return None

    @property
    def current_user(self):
        """The handler's current_user."""
        return self.r_handler.current_user

    @property
    def content_type(self):
        """The format specified in the request."""
        return self._query_arg('format', default='json').lower()

    @property
    def query_modifiers_applied(self):
        """Whether there were any modifiers applied to the query."""
        modifiers = set(self.request.arguments)
        modifiers.discard('format')
        modifiers.discard('dialect')
        return bool(modifiers)

    def _set_filename(self, filename, extension):
        now = datetime.datetime.now().isoformat()
        filename += '_' + now
        if self.query_modifiers_applied:
            filename += '_modified'
        self.ref_rh.set_header(
            'Content-Disposition',
            'inline; filename={}.{}'.format(
                filename_safe(filename), extension
            )
        )

    def _get_model(self, model_id, model_cls=None, exception=None):
        """Get an instance of this model class by id."""
        if model_cls is None:
            model_cls = self.resource_type
        return get_model(self.session, model_cls, model_id, exception)

    def _query_arg(self, argument_name, output=None, default=None):
        """Get a useful query parameter argument."""
        arg = self.r_handler.get_query_argument(argument_name, None)

        # Return default if the argument was not given.
        if not arg:
            return arg if arg == 0 else default

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

    def build_response(self, data, status=200):
        """Finish the Tornado response.

        This takes into account non-JSON content-types.
        """
        if self.content_type == 'csv':
            content_type = 'text/csv'
        else:
            content_type = 'application/json'
        self.ref_rh.set_header(
            'Content-Type', '{}; charset=UTF-8'.format(content_type)
        )
        self.ref_rh.set_status(status)
        self.ref_rh.finish(data)

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
        elif isinstance(err, NoResultFound):
            err = exc.NotFound()
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
            (self.objects_key, data[2]),
            ('total_entries', data[1]),
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
            if self.request_method() not in {'GET', 'HEAD', 'OPTIONS'}:
                self._check_xsrf_cookie()
            return True

        # An Administrator can log in with a token.
        try:
            token = self.r_handler.request.headers['Token']
            email = self.r_handler.request.headers['Email']
        except KeyError:
            return False
        # Get the user's token hash and expiration time.
        try:
            user = (
                self.session
                .query(Administrator.token, Administrator.token_expiration)
                .join(Email)
                .filter(Email.address == email)
                .one()
            )
        except NoResultFound:
            return False
        if user.token is None:
            return False
        if user.token_expiration.timetuple() < localtime():
            return False
        return bcrypt_sha256.verify(token, user.token)

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
        return self._specific_fields(self._get_model(model_id))

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

        default_sort = ['{}:ASC'.format(self.default_sort_column_name)]
        order_by_text = (
            element.split(':') for element in self._query_arg(
                'order_by', list, default=default_sort
            )
        )

        type_constraint = self._query_arg('type')
        user_id = self._query_arg('user_id')

        num_total = self.session.query(func.count(self.resource_type.id))
        if user_id is not None:
            if model_cls is Submission:
                num_total = num_total.join(Survey.submissions)
            num_total = (
                num_total
                .outerjoin(_administrator_table)
                .filter(administrator_filter(user_id))
            )
        num_total = num_total.scalar()

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

        if user_id is not None:
            if model_cls is Submission:
                query = query.join(Survey.submissions)
            query = (
                query
                .outerjoin(_administrator_table)
                .filter(administrator_filter(user_id))
            )

        if not deleted:
            query = query.filter(~model_cls.deleted)

        if type_constraint is not None:
            query = query.filter(model_cls.type_constraint == type_constraint)

        if where is not None:
            query = query.filter(where)

        for attribute_name, direction in order_by_text:
            try:
                order = getattr(model_cls, attribute_name)
            except AttributeError:
                order = text(
                    '{} {} NULLS LAST'.format(attribute_name, direction)
                )
            else:
                directions = {'asc': order.asc, 'desc': order.desc}
                order = directions[direction.lower()]().nullslast()
            query = query.order_by(order)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        result = query.all()
        if result:
            num_filtered = result[0][1]
            models = [res[0] for res in result]
            result = self._specific_fields(models, is_detail=False)
            return num_filtered, num_total, result
        return 0, num_total, []

    def update(self, model_id):
        """Update a model."""
        model = self._get_model(model_id)
        with self.session.begin():
            for attribute, value in self.data.items():
                setattr(model, attribute, value)
        return model

    def delete(self, model_id):
        """Set the deleted attribute to True. Does not destroy the instance."""
        model = self._get_model(model_id)
        with self.session.begin():
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
        """
        for prop in sorted(self.r_handler.request.arguments):
            prop_value = self.r_handler.get_query_argument(prop)
            if prop_value.isdigit():
                prop_value = int(prop_value)
            response[prop] = prop_value

        return response
