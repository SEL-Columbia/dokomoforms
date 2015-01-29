"""API endpoints dealing with aggregations."""
from tornado.escape import json_encode

import api.aggregation
from pages.util.base import APIHandler, get_email


class MinAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.min(question_id, email=get_email(self))
        self.write(json_encode(response))


class MaxAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.max(question_id, email=get_email(self))
        self.write(json_encode(response))


class SumAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.sum(question_id, email=get_email(self))
        self.write(json_encode(response))


class CountAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.count(question_id, email=get_email(self))
        self.write(json_encode(response))


class AvgAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.avg(question_id, email=get_email(self))
        self.write(json_encode(response))


class StddevPopAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.stddev_pop(question_id,
                                              email=get_email(self))
        self.write(json_encode(response))


class StddevSampAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.stddev_samp(question_id,
                                               email=get_email(self))
        self.write(json_encode(response))


# class ModeAPIHandler(APIHandler):
# def get(self, question_id: str):
# response = api.aggregation.mode(question_id, email=get_email(self))
# self.write(json_encode(response))

class TimeSeriesAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.time_series(question_id,
                                               email=get_email(self))
        self.write(json_encode(response))


class BarGraphAPIHandler(APIHandler):
    def get(self, question_id: str):
        response = api.aggregation.bar_graph(question_id,
                                             email=get_email(self))
        self.write(json_encode(response))
