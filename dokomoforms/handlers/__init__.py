"""All the Tornado RequestHandlers used in Dokomo Forms."""
from dokomoforms.handlers.root import Index, NotFound
from dokomoforms.handlers.auth import Login, Logout, GenerateToken
from dokomoforms.handlers.view.admin import (
    ViewSurveyHandler, ViewSurveyDataHandler,
    ViewSubmissionHandler
)
from dokomoforms.handlers.view.enumerate import Enumerate, EnumerateTitle
from dokomoforms.handlers.debug import (
    DebugUserCreationHandler, DebugLoginHandler, DebugLogoutHandler,
    DebugPersonaHandler, DebugRevisitHandler, DebugToggleRevisitHandler
)

__all__ = (
    'Index', 'NotFound',
    'Login', 'Logout', 'GenerateToken',
    'ViewSurveyHandler', 'ViewSurveyDataHandler',
    'ViewSubmissionHandler', 'Enumerate', 'EnumerateTitle',
    'DebugUserCreationHandler', 'DebugLoginHandler', 'DebugLogoutHandler',
    'DebugPersonaHandler', 'DebugRevisitHandler', 'DebugToggleRevisitHandler'
)
