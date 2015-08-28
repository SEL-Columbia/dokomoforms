"""All the Tornado RequestHandlers used in Dokomo Forms."""

from dokomoforms.handlers.root import Index, NotFound
from dokomoforms.handlers.auth import Login, Logout, GenerateToken
from dokomoforms.handlers.view.admin import (
    ViewHandler, ViewSurveyHandler, ViewSurveyDataHandler,
    ViewSubmissionHandler,
    VisualizationHandler,
)
from dokomoforms.handlers.view.enumerate import Enumerate, EnumerateTitle
from dokomoforms.handlers.debug import (
    DebugUserCreationHandler, DebugLoginHandler, DebugLogoutHandler,
    DebugPersonaHandler, DebugRevisitHandler
)

__all__ = (
    'Index', 'NotFound',
    'Login', 'Logout', 'GenerateToken',
    'ViewHandler', 'ViewSurveyHandler', 'ViewSurveyDataHandler',
    'ViewSubmissionHandler', 'VisualizationHandler',
    'Enumerate', 'EnumerateTitle',
    'DebugUserCreationHandler', 'DebugLoginHandler', 'DebugLogoutHandler',
    'DebugPersonaHandler', 'DebugRevisitHandler',
)
