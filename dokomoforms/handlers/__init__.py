"""All the Tornado RequestHandlers used in Dokomo Forms."""
from dokomoforms.handlers.root import Index, NotFound

from dokomoforms.handlers.user.admin import (
    AdminHomepageHandler,
    ViewSurveyHandler, ViewSurveyDataHandler,
    ViewSubmissionHandler, ViewUserAdminHandler
)
from dokomoforms.handlers.auth import (
    Login, Logout, GenerateToken, CheckLoginStatus
)
from dokomoforms.handlers.user.enumerate import (
    EnumerateHomepageHandler, Enumerate, EnumerateTitle
)
from dokomoforms.handlers.debug import (
    DebugUserCreationHandler, DebugLoginHandler, DebugLogoutHandler,
    DebugPersonaHandler, DebugRevisitHandler, DebugToggleRevisitHandler,
    DebugToggleRevisitSlowModeHandler
)
from dokomoforms.handlers.demo import (
    DemoUserCreationHandler, DemoLogoutHandler
)

__all__ = (
    'Index', 'NotFound',
    'Login', 'Logout', 'GenerateToken',
    'AdminHomepageHandler', 'CheckLoginStatus',
    'Login', 'Logout', 'GenerateToken',
    'ViewSurveyHandler', 'ViewSurveyDataHandler', 'ViewUserAdminHandler',
    'ViewSubmissionHandler',
    'EnumerateHomepageHandler', 'Enumerate', 'EnumerateTitle',
    'DebugUserCreationHandler', 'DebugLoginHandler', 'DebugLogoutHandler',
    'DebugPersonaHandler', 'DebugRevisitHandler', 'DebugToggleRevisitHandler',
    'DebugToggleRevisitSlowModeHandler',
    'DemoUserCreationHandler', 'DemoLogoutHandler'
)
