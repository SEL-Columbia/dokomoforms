""" UI utility methods for templates """

import tornado.web
import api.survey
import os.path

""" handler is implictly supplied somehow? """

def get_survey_info(handler, user, count):
        return [(survey["survey_id"], survey["title"])
                for survey in api.survey.get_all(user)[:count]]

def get_current_user(handler):
    current_user = ""
    if handler.current_user:
        current_user = handler.current_user.decode('utf-8')

    return current_user

def get_uri(handler, path=""):
    return os.path.join(handler.request.uri, path)
