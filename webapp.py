#!/usr/bin/env python

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.

"""

import tornado.web
import tornado.ioloop

import settings

from utils.logger import setup_custom_logger
logger = setup_custom_logger('dokomo')


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
    
    def post(self):
        uuid = self.get_argument('uuid')
        data = json.loads(self.get_argument('data'))



config = {
    'template_path': 'static',
    'static_path': 'static',
    'xsrf_cookies': False,
    'debug': True
}

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
