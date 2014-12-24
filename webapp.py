#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.
"""
import functools
import json
import urllib.parse
from tornado import httpclient

import tornado.web
import tornado.ioloop

import api.survey
import api.submission
import api.api_token
import api.user
from db.auth_user import verify_api_token, get_auth_user_by_email
from db.survey import AUTH_USER_ID
import settings
from utils.logger import setup_custom_logger


logger = setup_custom_logger('dokomo')


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        """Common handler functions here (e.g. user auth, template helpers)"""
        return self.get_secure_cookie('user')


class Index(BaseHandler):
    def get(self):
        survey = api.survey.get_one(settings.SURVEY_ID)
        self.xsrf_token  # need to access it in order to set it...
        self.render('index.html', survey=json.dumps(survey))

    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        self.write(api.submission.submit(data))


class CreateSurvey(BaseHandler):
    def get(self):
        self.render('viktor-create-survey.html')

    def post(self):
        self.write(api.survey.create({'title': self.get_argument('title')}))


class Surveys(BaseHandler):
    def get(self):
        surveys = api.survey.get_all(AUTH_USER_ID)
        self.write(json.dumps(surveys))

    def post(self):
        pass


class Survey(BaseHandler):
    def get(self, id):
        survey = api.survey.get_one(id)
        self.write(json.dumps(survey))

    def post(self, id):
        # Backward compatability for older browsers
        method = self.get_argument('_method', None)
        if method == 'DELETE':
            return self.delete(id)

        try:
            # Validate data
            data = json.loads(self.get_argument('data'))
            data['title']
            for question in data['questions']:
                question['title']
                question['type_constraint_name']
        except:
            raise tornado.web.HTTPError(400)

        survey = api.survey.create(data)
        self.write(json.dumps(survey))

    def delete(self, id):
        msg = api.survey.delete()
        self.write(json.dumps(msg))


class Submissions(BaseHandler):
    def get(self):
        submissions = api.submission.get_all()
        self.write(json.dumps(submissions))

    def post(self):
        pass


class FrontPage(BaseHandler):
    def get(self, *args, **kwargs):
        if self.get_current_user() is not None:
            self.render('profile-page.html')
        else:
            self.render('front-page.html')

class FreshXSRFTokenHandler(BaseHandler):
    def get(self):
        logged_in = self.get_current_user() is not None
        response = {'token': self.xsrf_token.decode('utf-8'),
                    'logged_in': logged_in}
        self.write(json.dumps(response))


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/user/login')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        assertion = self.get_argument('assertion')
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = 'https://verifier.login.persona.org/verify'
        data = {'assertion': assertion, 'audience': 'localhost:8888'}
        response = yield tornado.gen.Task(
            http_client.fetch,
            url,
            method='POST',
            body=urllib.parse.urlencode(data),
        )
        data = tornado.escape.json_decode(response.body)
        if data['status'] != "okay":
            raise tornado.web.HTTPError(400, "Failed assertion test")
        if not get_auth_user_by_email(data['email']):
            api.user.create_user({'email': data['email']})
        self.set_secure_cookie('user', data['email'], expires_days=1)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        response = {'next_url': '/'}
        self.write(tornado.escape.json_encode(response))
        self.finish()


class LoginPage(BaseHandler):
    def get(self):
        self.xsrf_token
        self.render('login.html')


class PageRequiringLogin(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.xsrf_token
        self.render('requires-login.html')


class APITokenGenerator(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # self.render('api-token.html')
        self.write(
            api.api_token.generate_token(
                {'email': self.get_current_user().decode('utf-8')}))


    @tornado.web.authenticated
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        self.write(api.api_token.generate_token(data))


def api_authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            token = self.request.headers['Token']
            email = self.request.headers['Email']
            if not verify_api_token(token=token, email=email):
                raise tornado.web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


class SurveysAPI(BaseHandler):
    @api_authenticated
    def get(self):
        surveys = api.survey.get_all(
            {'email': self.current_user.decode('utf-8')})
        self.write(json.dumps(surveys))


class LogoutHandler(BaseHandler):
    def get(self):
        self.redirect('/user/login')

    def post(self):
        self.clear_cookie('user')


config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': True,
    'login_url': '/user/login',
    'cookie_secret': settings.COOKIE_SECRET,
    'debug': True  # Remove this
}


if __name__ == '__main__':
    app = tornado.web.Application([
        (r'/', Index),
        (r'/surveys', Surveys),
        (r'/surveys/(.+)', Survey),
        (r'/surveys/(.+)/submissions', Submissions),
        (r'/user', FrontPage),
        (r'/user/requires-login', PageRequiringLogin),
        (r'/user/viktor-create-survey', CreateSurvey),
        (r'/user/login', LoginPage),
        (r'/user/login/persona', LoginHandler),
        (r'/user/logout', LogoutHandler),
        (r'/user/csrf-token', FreshXSRFTokenHandler),
        (r'/user/generate-api-token', APITokenGenerator),
        (r'/user/surveys', SurveysAPI)
    ], **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port ' + str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()


