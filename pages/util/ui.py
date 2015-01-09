""" UI utility methods for templates """

import os.path

import api.survey


""" handler is implictly supplied somehow? """


def get_survey_info(handler, user, count):
    return [(survey["survey_id"], survey["title"])
            for survey in api.survey.get_all(user)[:count]]


def get_uri(handler, path=""):
    return os.path.join(handler.request.uri, path)
