"""All the Tornado RequestHandlers used in Dokomo Forms."""
from dokomoforms.handlers.root import Index, FirstRun, NotFound
from dokomoforms.handlers.auth import Login, Logout, GenerateToken
from dokomoforms.handlers.view.admin import (
    ViewSurveyHandler, ViewSurveyDataHandler,
    ViewSubmissionHandler, ViewUserAdminHandler
)
from dokomoforms.handlers.view.enumerate import Enumerate, EnumerateTitle
from dokomoforms.handlers.debug import (
    DebugUserCreationHandler, DebugLoginHandler, DebugLogoutHandler,
    DebugPersonaHandler, DebugRevisitHandler, DebugToggleRevisitHandler,
    DebugToggleRevisitSlowModeHandler
)
from dokomoforms.handlers.demo import (
    DemoUserCreationHandler, DemoLogoutHandler
)

__all__ = (
    'Index', 'FirstRun', 'NotFound',
    'Login', 'Logout', 'GenerateToken',
    'ViewSurveyHandler', 'ViewSurveyDataHandler', 'ViewUserAdminHandler',
    'ViewSubmissionHandler', 'Enumerate', 'EnumerateTitle',
    'DebugUserCreationHandler', 'DebugLoginHandler', 'DebugLogoutHandler',
    'DebugPersonaHandler', 'DebugRevisitHandler', 'DebugToggleRevisitHandler',
    'DebugToggleRevisitSlowModeHandler',
    'DemoUserCreationHandler', 'DemoLogoutHandler'
)
