#!/usr/bin/env python

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.

"""

from sqlalchemy import Table, Metadata, create_engine

import tornado.web
import tornado.ioloop
import json

import settings

from utils.logger import setup_custom_logger
logger = setup_custom_logger('dokomo')


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
    
    def post(self):
        # viktor here, uuid may be absorbed into data
        uuid = self.get_argument('uuid')
        data = json.loads(self.get_argument('data'))

        survey_table = Table('survey', MetaData(bind=engine))
        # Hard code survey id... for now
        # TODO: fix it 
        # TODO: pep8
        survey = survey_table.select().where(survey_table.c.survey_id=='bcf89427-87d4-43ba-807e-9ffc8a095759').execute().first()
        



config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': False,
    'debug': True
}

# Good old database
engine = create_engine(settings.CONNECTION_STRING, convert_unicode=True)

def startserver():
    """It's good practice to put all the startup logic
    in a class or function, invoked via '__main__'
    instead of just starting on import, which, among
    other things, fubars the tests"""

    app = tornado.web.Application([
        (r'/', Index)
    ], **config)
    app.listen(settings.WEBAPP_PORT, '0.0.0.0')

    logger.info('starting server on port '+str(settings.WEBAPP_PORT))

    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    startserver()
