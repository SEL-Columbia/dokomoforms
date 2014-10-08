#!/usr/bin/env python3

"""
This tornado server creates the client app by serving html/css/js and
it also functions as the wsgi container for accepting survey form post
requests back from the client app.

"""

import tornado.web
import tornado.ioloop

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

app = tornado.web.Application([
    (r'/', Index)
], **config)
app.listen(8888, '0.0.0.0')

logger.info('starting server on port 8888')

tornado.ioloop.IOLoop.current().start()

