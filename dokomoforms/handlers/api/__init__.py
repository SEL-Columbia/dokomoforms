"""Handlers for the API endpoints."""
from dokomoforms.handlers.api.serializer import ModelJSONSerializer

from dokomoforms.handlers.api.base import BaseResource
from dokomoforms.handlers.api.surveys import (
    SurveyResource, get_survey_for_handler
)
from dokomoforms.handlers.api.submissions import (
    SubmissionResource, get_submission_for_handler
)
from dokomoforms.handlers.api.nodes import NodeResource
from dokomoforms.handlers.api.users import UserResource
from dokomoforms.handlers.api.photos import PhotoResource


__all__ = (
    'ModelJSONSerializer',

    'BaseResource',

    'SurveyResource', 'get_survey_for_handler',
    'SubmissionResource', 'get_submission_for_handler',
    'UserResource',
    'NodeResource',
    'PhotoResource',
)
