"""Handlers for the API endpoints."""
from dokomoforms.handlers.api.v0.serializer import ModelJSONSerializer

from dokomoforms.handlers.api.v0.base import BaseResource
from dokomoforms.handlers.api.v0.surveys import (
    SurveyResource, get_survey_for_handler
)
from dokomoforms.handlers.api.v0.submissions import (
    SubmissionResource, get_submission_for_handler
)
from dokomoforms.handlers.api.v0.nodes import NodeResource
from dokomoforms.handlers.api.v0.users import UserResource
from dokomoforms.handlers.api.v0.photos import PhotoResource


__all__ = (
    'ModelJSONSerializer',

    'BaseResource',

    'SurveyResource', 'get_survey_for_handler',
    'SubmissionResource', 'get_submission_for_handler',
    'UserResource',
    'NodeResource',
    'PhotoResource',
)
