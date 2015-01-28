"""API endpoints dealing with aggregations."""
from tornado.escape import json_encode

import api.aggregation
from pages.util.base import APIHandler, get_email


class MinAPI(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.min(question_id, email=get_email(self))
        self.write(json_encode(response))


class MaxAPI(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.max(question_id, email=get_email(self))
        self.write(json_encode(response))


class SumAPI(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.sum(question_id, email=get_email(self))
        self.write(json_encode(response))


class CountAPI(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.count(question_id, email=get_email(self))
        self.write(json_encode(response))
