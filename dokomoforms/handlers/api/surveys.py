"""Surveys API handlers."""

import tornado.web
import tornado.gen
import tornado.httpclient
from tornado.escape import json_decode, json_encode

from dokomoforms.handlers.util import BaseAPIHandler


class SurveysAPIList(BaseAPIHandler):
    def get(self):
        self.write(json_encode({
            "offset": 5,
            "limit": 1,
            "filtered_entries": 34839,
            "total_entries": 40629,
            "surveys": [
                {
                    "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
                    "survey_metadata": {
                        "location": {
                            "lon": 5.118915,
                            "lat": 7.353078
                        },
                        "author": "Abdizzle",
                        "organization": "SEL"
                    },
                    "questions": [
                        {
                            "sequence_number": 1,
                            "type_constraint_name": "integer",
                            "question_title": "integer question",
                            "question_id": "8bea838c-9373-410a-8510-cfda70469115",
                            "hint": "",
                            "logic": {
                                "allow_other": False,
                                "allow_dont_know": True,
                                "required": False
                            },
                            "allow_multiple": False,
                            "question_to_sequence_number": 2
                        },
                        {
                            "sequence_number": 2,
                            "type_constraint_name": "multiple_choice",
                            "question_title": "multiple choice question",
                            "question_id": "17d6976c-0bdc-4d72-accc-bfd8fc01be04",
                            "hint": "",
                            "logic": {
                                "allow_other": False,
                                "allow_dont_know": False,
                                "required": False
                            },
                            "allow_multiple": False,
                            "branches": [
                                {
                                    "question_choice_id": "1feba851-c431-479a-8c38-c26c0128427b",
                                    "to_question_id": "6510f6c5-860e-4b06-ae73-76af2b1ecea9",
                                    "to_sequence_number": 3
                                },
                                {
                                    "question_choice_id": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
                                    "to_question_id": "3ba907ca-f80c-419f-a893-0745dae8e35c",
                                    "to_sequence_number": 4
                                }
                            ],
                            "question_to_sequence_number": 3,
                            "choices": [
                                {
                                    "choice": "choice 1",
                                    "question_choice_id": "1feba851-c431-479a-8c38-c26c0128427b",
                                    "choice_number": 1
                                },
                                {
                                    "choice": "choice 2",
                                    "question_choice_id": "30d6aed1-ef7f-4db9-b4c1-fcbdfb99de2c",
                                    "choice_number": 2
                                }
                            ]
                        },
                        {
                            "sequence_number": 3,
                            "type_constraint_name": "decimal",
                            "question_title": "decimal question",
                            "question_id": "6510f6c5-860e-4b06-ae73-76af2b1ecea9",
                            "hint": "",
                            "logic": {
                                "allow_other": False,
                                "allow_dont_know": False,
                                "required": False
                            },
                            "allow_multiple": False,
                            "question_to_sequence_number": 4
                        }
                    ],
                    "survey_title": "test_title",
                    "survey_version": 0,
                    "created_on": "2015-04-23T20:39:40.419031+00:00",
                    "last_updated": "2015-04-23T20:39:40.419031+00:00"
                }
            ]
        }))


class SurveysAPISingle(BaseAPIHandler):

    def get(self, survey_id=None):
        self.write(json_encode({
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "survey_metadata": {
                "location": {
                    "lon": 5.118915,
                    "lat": 7.353078
                },
                "author": "Abdizzle",
                "organization": "SEL"
            },
            "questions": [
                {
                    "sequence_number": 1,
                    "type_constraint_name": "integer",
                    "question_title": "integer question",
                    "question_id": "8bea838c-9373-410a-8510-cfda70469115",
                    "hint": "",
                    "logic": {
                        "allow_other": False,
                        "allow_dont_know": True,
                        "required": False
                    },
                    "allow_multiple": False,
                    "question_to_sequence_number": 2
                }
            ],
            "survey_title": "test_title",
            "survey_version": 0,
            "created_on": "2015-04-23T20:39:40.419031+00:00",
            "last_updated": "2015-04-23T20:39:40.419031+00:00"
        }))
