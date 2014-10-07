import logging

import tornado.web
import tornado.ioloop


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
    
    def post(self):
        uuid = self.get_argument('uuid')
        data = json.loads(self.get_argument('data'))
        data['uuid'] = uuid
        
        (db.table('facilities')
            .insert(data)
            .run())


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

print('starting server on port 8888')

logging.getLogger().setLevel(logging.INFO)
tornado.ioloop.IOLoop.current().start()

