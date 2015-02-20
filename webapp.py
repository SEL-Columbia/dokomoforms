#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""
from sqlalchemy import create_engine

from tornado.escape import json_encode
import tornado.web
import tornado.ioloop

import api.aggregation
import api.survey
import api.submission
import api.user
from db import engine
from pages.api.aggregations import AggregationHandler
from pages.auth import LogoutHandler, LoginHandler
from pages.api.submissions import SubmissionsAPIHandler, \
    SingleSubmissionAPIHandler, SubmitAPIHandler
from pages.api.surveys import SurveysAPIHandler, SingleSurveyAPIHandler, \
    CreateSurveyAPIHandler
from pages.util.base import BaseHandler, get_json_request_body
import pages.util.ui
from pages.debug import DebugLoginHandler, DebugLogoutHandler, \
    DebugUserCreationHandler
from pages.view.surveys import ViewHandler
from pages.view.submissions import ViewSubmissionsHandler, \
    ViewSubmissionHandler
from pages.view.visualize import VisualizationHandler
import settings
from utils.logger import setup_custom_logger
from db.survey import SurveyPrefixDoesNotIdentifyASurveyError, \
    SurveyPrefixTooShortError, \
    get_survey_id_from_prefix, get_surveys_by_email


logger = setup_custom_logger('dokomo')


class Index(BaseHandler):
    def get(self, msg=""):
        surveys = get_surveys_by_email(self.current_user, 10)
        self.render('index.html', message=msg, surveys=surveys)

    def post(self):
        LogoutHandler.post(self)  # TODO move to js
        self.get("You logged out")


class Survey(BaseHandler):
    def get(self, survey_prefix: str):
        try:
            survey_id = get_survey_id_from_prefix(survey_prefix)
            if len(survey_prefix) < 36:
                self.redirect('/survey/{}'.format(survey_id), permanent=False)
            else:
                survey = api.survey.display_survey(survey_id)['result']
                self.render('survey.html',
                            survey=json_encode(survey),
                            survey_title=survey['survey_title'])
        except (SurveyPrefixDoesNotIdentifyASurveyError,
                SurveyPrefixTooShortError):
            raise tornado.web.HTTPError(404)

    def post(self, uuid):
        SubmitAPIHandler.post(self, uuid)  # TODO: Hey Abdi kill this


class APITokenGenerator(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.render('api-token.html')
        self.write(
            api.user.generate_token(
                {'email': self.current_user}))

    @tornado.web.authenticated
    def post(self):
        data = get_json_request_body(self)
        self.write(api.user.generate_token(data))


use_xsrf_cookies = True
# If TEST_USER is set, don't use XSRF tokens
try:
    _ = settings.TEST_USER
    use_xsrf_cookies = False
except AttributeError:
    pass

config = {
    'template_path': 'templates',
    'static_path': 'static',
    'xsrf_cookies': use_xsrf_cookies,
    'login_url': '/',
    'cookie_secret': settings.COOKIE_SECRET,
    'ui_methods': pages.util.ui,
    'debug': settings.APP_DEBUG
}

UUID_REGEX = '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][' \
             'a-f0-9]{3}-?[a-f0-9]{12}'

handlers = [
    # Dokomo Forms
    (r'/', Index),

    # View surveys and submissions
    (r'/view/?', ViewHandler),
    (r'/view/({})/?'.format(UUID_REGEX), ViewSubmissionsHandler),
    (r'/view/submission/({})/?'.format(UUID_REGEX),
     ViewSubmissionHandler),

    (r'/visualize/({})/?'.format(UUID_REGEX), VisualizationHandler),

    # Survey Submissions
    (r'/survey/(.+)/?', Survey),

    # Auth
    (r'/user/login/persona/?', LoginHandler),  # Post to Persona here

    # API tokens
    (r'/user/generate-api-token/?', APITokenGenerator),

    # JSON API
    (r'/api/aggregate/({})/?'.format(UUID_REGEX), AggregationHandler),
    (r'/api/surveys/?', SurveysAPIHandler),
    (r'/api/surveys/create/?', CreateSurveyAPIHandler),
    (r'/api/surveys/({})/?'.format(UUID_REGEX),
     SingleSurveyAPIHandler),
    (r'/api/surveys/({})/submit/?'.format(UUID_REGEX),
     SubmitAPIHandler),
    (r'/api/surveys/({})/submissions/?'.format(UUID_REGEX),
     SubmissionsAPIHandler),
    (r'/api/submissions/({})/?'.format(UUID_REGEX),
     SingleSubmissionAPIHandler),
]

if config.get('debug', False):
    handlers += [(r'/debug/create/(.+)/?', DebugUserCreationHandler),
                 (r'/debug/login/(.+)/?', DebugLoginHandler),
                 (r'/debug/logout/?', DebugLogoutHandler), ]

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, pages, **config)

        self.connection = engine.connect()


app = Application()

if __name__ == '__main__':
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().set_blocking_log_threshold(1)
    tornado.ioloop.IOLoop.current().start()
