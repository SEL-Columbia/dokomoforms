"""All the Tornado RequestHandlers used in Dokomo Forms."""

from dokomoforms.handlers.root import Index, NotFound
from dokomoforms.handlers.auth import Login, Logout, GenerateToken
from dokomoforms.handlers.view.admin import (
    ViewHandler, ViewSurveyHandler, ViewSurveyDataHandler,
    ViewSubmissionHandler,
    VisualizationHandler,
)
from dokomoforms.handlers.view.enumerate import Enumerate
from dokomoforms.handlers.debug import (
    DebugUserCreationHandler, DebugLoginHandler, DebugLogoutHandler
)

__all__ = (
    'ViewHandler', 'ViewSurveyHandler', 'ViewSurveyDataHandler',
    'ViewSubmissionHandler',
    'VisualizationHandler',

    'Enumerate',
    'Index', 'NotFound',
    'Login', 'Logout', 'GenerateToken',
    'DebugUserCreationHandler', 'DebugLoginHandler', 'DebugLogoutHandler'
)
