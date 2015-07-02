"""Handlers for the API endpoints."""
from dokomoforms.api.serializer import ModelJSONSerializer

from dokomoforms.api.base import BaseResource
from dokomoforms.api.surveys import SurveyResource
from dokomoforms.api.submissions import SubmissionResource
from dokomoforms.api.nodes import NodeResource


__all__ = (
    'ModelJSONSerializer',

    'BaseResource',

    'SurveyResource',
    'SubmissionResource',
    'NodeResource',

)
