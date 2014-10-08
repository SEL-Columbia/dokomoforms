
"""
Tests for the dokomo webapp

"""

import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web

import unittest

from webapp import Index, config

class TestDokomoWebapp(unittest.TestCase):
    http_server = None
    response = None

    def setUp(self):
        application = tornado.web.Application([
                (r'/', Index), 
                ], **config)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(8888)

    def tearDown(self):
        self.http_server.stop()

    def handle_request(self, response):
        self.response = response
        tornado.ioloop.IOLoop.instance().stop()

    def testGetIndex(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        http_client.fetch('http://localhost:8888/', self.handle_request)
        tornado.ioloop.IOLoop.instance().start()
        self.failIf(self.response.error)
        # Test contents of response
        self.assertIn("<title>Ebola Response</title>", self.response.body)

if __name__ == '__main__':
    unittest.main()
