"""Handlers for the API endpoints."""
from dokomoforms.api.serializer import ModelJSONSerializer

from dokomoforms.api.base import BaseResource
from dokomoforms.api.surveys import SurveyResource, get_survey_for_handler
from dokomoforms.api.submissions import (
    SubmissionResource, get_submission_for_handler
)
from dokomoforms.api.nodes import NodeResource
from dokomoforms.api.photos import PhotoResource


__all__ = (
    'ModelJSONSerializer',

    'BaseResource',

    'SurveyResource', 'get_survey_for_handler',
    'SubmissionResource', 'get_submission_for_handler',
    'NodeResource',
    'PhotoResource',
)
