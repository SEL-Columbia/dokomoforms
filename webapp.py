#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.

"""

import json
import urllib.parse
from tornado import httpclient

import tornado.web
import tornado.ioloop

import api.survey
import api.submission
import settings
from utils.logger import setup_custom_logger


logger = setup_custom_logger('dokomo')


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('user')

class FreshXSRFTokenHandler(BaseHandler):
    def get(self):
        logged_in = self.get_current_user() is not None
        response = {'token': self.xsrf_token.decode('utf-8'),
                    'logged_in': logged_in}
        self.write(json.dumps(response))

class Index(tornado.web.RequestHandler):
    def get(self):
        survey = api.survey.get_one(settings.SURVEY_ID)
        self.xsrf_token  # need to access it in order to set it...
        self.render('index.html', survey=json.dumps(survey))

    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        self.write(api.submission.submit(data))


class LoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        assertion = self.get_argument('assertion')
        http_client = httpclient.AsyncHTTPClient()
        domain = 'localhost:8888'  # MAKE SURE YOU CHANGE THIS
        url = 'https://verifier.login.persona.org/verify'
        data = {'assertion': assertion, 'audience': domain}
        response = http_client.fetch(
            url,
            method='POST',
            body=urllib.parse.urlencode(data),
            callback=self._on_response
        )

    def _on_response(self, response):
        struct = tornado.escape.json_decode(response.body)
        if struct['status'] != 'okay':
            raise tornado.web.HTTPError(400, "Failed assertion test")
        email = struct['email']
        self.set_secure_cookie('user', email,
                               expires_days=1)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        response = {'next_url': '/'}
        self.write(tornado.escape.json_encode(response))
        self.finish()


class CreateSurvey(tornado.web.RequestHandler):
    def get(self):
        self.render('viktor-create-survey.html')

    def post(self):
        self.write(api.survey.create({'title': self.get_argument('title')}))


class LoginPage(BaseHandler):
    def get(self):
        self.xsrf_token
        self.render('login.html')


class PageRequiringLogin(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.xsrf_token
        self.render('requires-login.html')


class LogoutHandler(BaseHandler):
    def get(self):
        self.redirect('/login')

    def post(self):
        self.clear_cookie('user')



config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': True,
    'login_url': '/login',
    'cookie_secret': settings.COOKIE_SECRET,
    'debug': True  # Remove this
}

# Good old database
# engine = create_engine(settings.CONNECTION_STRING, convert_unicode=True)

def startserver():
    """It's good practice to put all the startup logic
    in a class or function, invoked via '__main__'
    instead of just starting on import, which, among
    other things, fubars the tests"""

    app = tornado.web.Application([
                                      (r'/', Index),
                                      (r'/login', LoginPage),
                                      (r'/login/persona', LoginHandler),
                                      (r'/logout', LogoutHandler),
                                      (r'/viktor-create-survey', CreateSurvey),
                                      (r'/requires-login', PageRequiringLogin),
                                      (r'/csrf-token', FreshXSRFTokenHandler)
                                  ], **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    startserver()
