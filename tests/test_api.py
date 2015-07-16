"""API tests"""
from collections import OrderedDict
from datetime import datetime, date, timedelta
import json
import uuid
import unittest

import dateutil.parser

from passlib.hash import bcrypt_sha256

from tornado.escape import json_decode, json_encode

from tests.util import DokoHTTPTest, setUpModule, tearDownModule

from dokomoforms.models import Submission, Survey, Node, SurveyCreator
import dokomoforms.models as models
from dokomoforms.api.base import BaseResource
from dokomoforms.api.nodes import NodeResource

utils = (setUpModule, tearDownModule)


"""
TODO:
- add exception and error response tests
    - add error tests for unauthenticated users
        - creating surveys
- add tests for total_entries and filtered_entries
- add tests for sub_surveys
"""

# The numbers expected to be present via fixtures
TOTAL_SURVEYS = 14
TOTAL_SUBMISSIONS = 112
TOTAL_NODES = 16


class TestErrorHandling(DokoHTTPTest):
    def test_bad_value_type(self):
        # url to test
        offset = 'five'
        url = self.api_root + '/surveys'
        query_params = {
            'offset': offset
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn(
            'invalid', json_decode(response.body)['error'],
            msg=json_decode(response.body)
        )

    def test_not_found(self):
        survey_id = str(uuid.uuid4())
        # url to tests
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.assertEqual(response.code, 404)
        self.assertIn('not found', json_decode(response.body)['error'])


class TestApiBase(unittest.TestCase):
    def test_current_user(self):
        """Doesn't really test anything... it might in the future."""
        fake_r_handler = lambda: None
        fake_r_handler.current_user = 'test'
        br = NodeResource()
        br.ref_rh = fake_r_handler
        self.assertEqual(br.current_user, 'test')


class TestAuthentication(DokoHTTPTest):
    def test_bounce(self):
        url = self.api_root + '/nodes'
        response = self.fetch(url, method='GET', _logged_in_user=None)
        self.assertEqual(response.code, 401)

    def test_is_authenticated_logged_in(self):
        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = object()
        fake_resource.r_handler = fake_r_handler
        self.assertTrue(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_api_token(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.token = bcrypt_sha256.encrypt('a').encode()
            user.token_expiration = datetime.now() + timedelta(days=1)
            self.session.add(user)

        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Token': 'a',
            'Email': 'test_creator@fixtures.com',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertTrue(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_wrong_user(self):
        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Token': 'b',
            'Email': 'wrong',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertFalse(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_missing_api_token(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.token = bcrypt_sha256.encrypt('a').encode()
            user.token_expiration = datetime.now() + timedelta(days=1)
            self.session.add(user)

        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Email': 'test_creator@fixtures.com',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertFalse(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_token_has_not_been_generated(self):
        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Token': 'b',
            'Email': 'test_creator@fixtures.com',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertFalse(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_wrong_api_token(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.token = bcrypt_sha256.encrypt('a').encode()
            user.token_expiration = datetime.now() + timedelta(days=1)
            self.session.add(user)

        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Token': 'b',
            'Email': 'test_creator@fixtures.com',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertFalse(BaseResource.is_authenticated(fake_resource))

    def test_is_authenticated_expired_api_token(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.token = bcrypt_sha256.encrypt('a').encode()
            user.token_expiration = datetime.now() - timedelta(days=1)
            self.session.add(user)

        fake_resource = lambda: None
        fake_r_handler = lambda: None
        fake_r_handler.current_user = None
        fake_request = lambda: None
        fake_request.headers = {
            'Token': 'a',
            'Email': 'test_creator@fixtures.com',
        }
        fake_r_handler.request = fake_request
        fake_resource.r_handler = fake_r_handler
        fake_resource.session = self.session

        self.assertFalse(BaseResource.is_authenticated(fake_resource))


class TestSurveyApi(DokoHTTPTest):
    """These tests are made against the known fixture data."""
    def test_list_surveys(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that the expected keys are present
        self.assertTrue('surveys' in survey_dict)

        self.assertEqual(len(survey_dict['surveys']), TOTAL_SURVEYS)

        # check that no error is present
        self.assertFalse("error" in survey_dict)

    def test_list_surveys_with_empty_limit(self):
        # url to test
        url = self.api_root + '/surveys?limit='
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that the expected keys are present
        self.assertTrue('surveys' in survey_dict)

        self.assertEqual(len(survey_dict['surveys']), TOTAL_SURVEYS)

        # check that no error is present
        self.assertFalse("error" in survey_dict)

    def test_list_surveys_with_offset(self):
        # url to test
        offset = 5
        url = self.api_root + '/surveys'
        query_params = {
            'offset': offset
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that the offset value comes back correctly
        self.assertTrue("offset" in survey_dict)
        self.assertEqual(survey_dict['offset'], offset)

        self.assertEqual(len(survey_dict['surveys']), TOTAL_SURVEYS - offset)
        # TODO: check the known value of the first survey
        # in the offset response

    def test_list_surveys_with_limit(self):
        # url to test
        url = self.api_root + '/surveys'
        query_params = {
            'limit': 1
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response

        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that the limit value comes back correctly
        self.assertTrue("limit" in survey_dict)
        self.assertEqual(survey_dict['limit'], 1)

        # check the number of surveys matches the limit
        self.assertEqual(len(survey_dict['surveys']), 1)

    def test_list_surveys_with_limit_and_bogus_parameter(self):
        # url to test
        url = self.api_root + '/surveys?limit=1&bbb=ccc'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response

        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that the limit value comes back correctly
        self.assertTrue("limit" in survey_dict)
        self.assertEqual(survey_dict['limit'], 1)

        # check the number of surveys matches the limit
        self.assertEqual(len(survey_dict['surveys']), 1)

    def test_get_single_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to tests
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('survey_type' in survey_dict)
        self.assertTrue('default_language' in survey_dict)
        self.assertTrue('deleted' in survey_dict)
        self.assertTrue('creator_name' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)
        self.assertTrue('creator_id' in survey_dict)
        self.assertTrue('version' in survey_dict)

        self.assertFalse("error" in survey_dict)

    def test_get_single_public_survey_without_logging_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to tests
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method, _logged_in_user=None)
        # test response
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertIn('id', survey_dict, msg=survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('survey_type' in survey_dict)
        self.assertTrue('default_language' in survey_dict)
        self.assertTrue('deleted' in survey_dict)
        self.assertTrue('creator_name' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)
        self.assertTrue('creator_id' in survey_dict)
        self.assertTrue('version' in survey_dict)

        self.assertFalse("error" in survey_dict)

    def test_cannot_get_enumerator_only_survey_without_logging_in(self):
        """TODO: Find out if this makes sense."""
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to tests
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method, _logged_in_user=None)
        self.assertEqual(response.code, 401)

    def test_get_single_survey_with_sub_surveys(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json_decode(response.body)

        survey_node = survey_dict['nodes'][0]
        sub_surveys = survey_node['sub_surveys']
        sub_survey = sub_surveys[0]

        # check that expected keys are present
        self.assertTrue('sub_surveys' in survey_node)

        self.assertTrue('deleted' in sub_survey)
        self.assertTrue('buckets' in sub_survey)
        self.assertTrue('repeatable' in sub_survey)
        self.assertTrue('nodes' in sub_survey)

        self.assertFalse("error" in survey_dict)

    def test_nested_sub_surveys(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json_decode(response.body)
        survey_node = survey_dict['nodes'][0]

        sub_surveys = survey_node['sub_surveys']
        sub_survey = sub_surveys[0]
        sub_sub_surveys = sub_survey['nodes'][0]['sub_surveys']
        sub_sub_survey = sub_sub_surveys[0]

        # check that expected keys are present
        self.assertTrue('sub_surveys' in survey_node)

        self.assertTrue('deleted' in sub_sub_survey)
        self.assertTrue('buckets' in sub_sub_survey)
        self.assertTrue('repeatable' in sub_sub_survey)
        self.assertTrue('nodes' in sub_sub_survey)

        self.assertFalse("error" in survey_dict)

    def test_create_survey_with_node_definition(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "survey_type": "public",
            "default_language": "English",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'node': {
                        "title": {"English": "test_time_node"},
                        "hint": {
                            "English": ""
                        },
                        "allow_multiple": False,
                        "allow_other": False,
                        "type_constraint": "time",
                        "logic": {},
                        "deleted": False
                    },
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201, msg=response.body)

        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('version' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)

        self.assertFalse("error" in survey_dict)

    def test_create_survey_with_required_question(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_type": "public",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'required': True,
                    'node': {
                        "title": {"English": "test_time_node"},
                        "type_constraint": "integer",
                    },
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201, msg=response.body)

    def test_create_survey_with_sub_survey(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_type": "public",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'required': True,
                    'node': {
                        "title": {"English": "test_time_node"},
                        "type_constraint": "integer",
                    },
                    'sub_surveys': [
                        {
                            'nodes': [
                                {
                                    'required': True,
                                    'node': {
                                        'id': (
                                            self.session
                                            .query(models.Question.id)
                                            .first()
                                        )
                                    },
                                },
                            ],
                            'buckets': [
                                {
                                    'bucket_type': 'integer',
                                    'bucket': '[1, 3]',
                                },
                            ],
                        },
                    ],
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201, msg=response.body)

    def test_create_survey_with_repeatable_sub_survey(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_type": "public",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'required': True,
                    'node': {
                        "title": {"English": "test_time_node"},
                        "type_constraint": "integer",
                    },
                    'sub_surveys': [
                        {
                            'repeatable': True,
                            'nodes': [
                                {
                                    'required': True,
                                    'node': {
                                        'allow_multiple': True,
                                        'type_constraint': 'integer',
                                        'title': {'English': 'a'}
                                    },
                                },
                            ],
                            'buckets': [
                                {
                                    'bucket_type': 'integer',
                                    'bucket': '[1, 3]',
                                },
                            ],
                        },
                    ],
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201, msg=response.body)

    def test_create_survey_with_nonsense_node_definition(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "survey_type": "public",
            "default_language": "English",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'node': {
                        "not a title": {"English": "test_time_node"},
                        "deleted": False
                    },
                },
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)

        # test response
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('missing', json_decode(response.body)['error'])

    def test_create_survey_with_node_id(self):
        node_id = "60e56824-910c-47aa-b5c0-71493277b43f"
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "survey_type": "public",
            "default_language": "English",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'node': {"id": node_id},
                },
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201, msg=response.body)

        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)
        survey_node = survey_dict['nodes'][0]

        # check that expected keys are present
        self.assertTrue('id' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('version' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)

        self.assertEqual(
            survey_node['node_id'], "60e56824-910c-47aa-b5c0-71493277b43f")

        self.assertFalse("error" in survey_dict)

    def test_create_enumerator_only_survey(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "survey_type": 'enumerator_only',
            "default_language": "English",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    'node': {
                        "title": {"English": "test_time_node"},
                        "hint": {
                            "English": ""
                        },
                        "allow_multiple": False,
                        "allow_other": False,
                        "type_constraint": "time",
                        "logic": {},
                        "deleted": False
                    },
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('version' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)

        self.assertFalse("error" in survey_dict)

    def test_update_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        self.assertFalse(
            self.session.query(Survey.deleted).filter_by(id=survey_id).scalar()
        )
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method
        method = 'PUT'
        # body
        body = {
            'deleted': True
        }
        encoded_body = json_encode(body)
        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 202)
        # test response
        self.assertTrue(json_decode(response.body)['deleted'])
        self.assertTrue(
            self.session.query(Survey.deleted).filter_by(id=survey_id).scalar()
        )

    def test_delete_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method
        method = 'DELETE'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # test response - successful DELETE returns 204 no content.
        self.assertEqual(response.code, 204)

        survey = self.session.query(Survey).get(survey_id)

        self.assertTrue(survey.deleted)

    def test_submit_to_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    def test_submit_to_survey_bogus_survey_id(self):
        survey_id = str(uuid.uuid4())
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 404, msg=response.body)

    def test_submit_to_survey_with_integer_answer_response(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "60e56824-910c-47aa-b5c0-71493277b43f",
                    "type_constraint": "integer",
                    "response": {
                        "response_type": "answer",
                        "response": 3
                    }
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertEqual(
            submission_dict['answers'][0]['response_type'], 'answer')
        self.assertEqual(submission_dict['answers'][0]['response'], 3)

    def test_submit_to_survey_with_multiple_choice_answer_response(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "80e56824-910c-47aa-b5c0-71493277b439",
                    "type_constraint": "multiple_choice",
                    "response": {
                        "response_type": "answer",
                        "response": "11156824-910c-47aa-b5c0-71493277b439"
                    }
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        # check answer
        self.assertEqual(
            submission_dict['answers'][0]['response_type'], 'answer')
        self.assertEqual(
            submission_dict['answers'][0]['response']['choice_number'], 1)
        self.assertEqual(
            submission_dict['answers']
            [0]['response']['choice_text']['English'], 'second choice')

    def test_submit_to_survey_with_other_response(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "80e56824-910c-47aa-b5c0-71493277b439",
                    "type_constraint": "multiple_choice",
                    "response": {
                        "response_type": "other",
                        "response": "bwop"
                    }
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertEqual(
            submission_dict['answers'][0]['response_type'], 'other')
        self.assertEqual(submission_dict['answers'][0]['response'], 'bwop')

    def test_submit_to_survey_with_dont_know_response(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "80e56824-910c-47aa-b5c0-71493277b439",
                    "type_constraint": "multiple_choice",
                    "response": {
                        "response_type": "dont_know",
                        "response": "bwop"
                    }
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertEqual(
            submission_dict['answers'][0]['response_type'], 'dont_know')
        self.assertEqual(submission_dict['answers'][0]['response'], 'bwop')

    def test_submit_to_public_survey_while_authenticated(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            # public survey, so unauthenticated submission type -- we'll check
            # that an enumerator_id comes back in the response
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        # The important part:
        self.assertTrue('enumerator_user_id' in submission_dict)
        self.assertTrue('enumerator_user_name' in submission_dict)

    def test_submit_to_enum_only_survey_while_authenticated(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "authenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    def test_error_public_submission_to_enum_only_survey(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))

        submission_dict = json_decode(response.body)

        self.assertTrue('error' in submission_dict)

        self.assertEqual(response.code, 400)

    def test_list_submissions_to_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submissions'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        submission_list = json_decode(response.body)

        self.assertIn('submissions', submission_list, msg=submission_list)
        self.assertTrue('survey_id' in submission_list)

        self.assertFalse('error' in submission_list)

    def test_get_stats_for_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/stats'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)

        stats = json_decode(response.body)

        # test response
        today = date.today()
        self.assertTrue(
            stats['latest_submission_time'].startswith(today.isoformat())
        )
        self.assertTrue(stats['created_on'].startswith(today.isoformat()))
        self.assertTrue(
            stats['earliest_submission_time'].startswith(
                (today - timedelta(days=99)).isoformat()
            )
        )
        self.assertEqual(stats['num_submissions'], 101)

    def test_get_stats_for_survey_not_logged_in(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/stats'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method, _logged_in_user=None)
        self.assertEqual(response.code, 401)

    def test_submission_activity_for_all_surveys(self):
        # url to test
        url = self.api_root + '/surveys/activity'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        activity = json_decode(response.body)
        self.assertIn('activity', activity, msg=activity)
        self.assertEqual(len(activity['activity']), 30)

        # test 'days' query param
        query_params = {
            'days': 10
        }
        url = self.append_query_params(url, query_params)
        response = self.fetch(url, method=method)
        activity = json_decode(response.body)
        self.assertIn('activity', activity, msg=activity)
        activity_list = activity['activity']
        self.assertEqual(len(activity_list), 10)
        self.assertEqual(activity_list[0]['num_submissions'], 13)
        self.assertTrue(all(
            act['num_submissions'] == 1 for act in activity_list[1:]
        ))

    def test_get_all_submission_activity(self):
        url = self.api_root + '/surveys/activity'
        query_params = {
            'days': 1000
        }
        url = self.append_query_params(url, query_params)
        response = self.fetch(url, method='GET')
        activity = json_decode(response.body)
        self.assertIn('activity', activity, msg=activity)
        activity_list = activity['activity']
        self.assertEqual(len(activity_list), 100)
        self.assertEqual(
            sum(act['num_submissions'] for act in activity_list),
            TOTAL_SUBMISSIONS
        )

    def test_submission_activity_for_single_surveys(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/activity'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        activity = json_decode(response.body)

        self.assertTrue('activity' in activity)
        self.assertEqual(len(activity['activity']), 30)

        # test 'days' query param
        query_params = {
            'days': 10
        }
        url = self.append_query_params(url, query_params)
        response = self.fetch(url, method=method)
        activity = json_decode(response.body)
        self.assertTrue('activity' in activity)
        self.assertEqual(len(activity['activity']), 10)

    # TODO: We probably eventually want surveys not to be totally public.
    # def test_survey_access_denied_for_unauthorized_user(self):
    #    # this survey is owned by a different creator
    #    survey_id = 'd0816b52-204f-41d4-aaf0-ac6ae2970923'

    #    # url to test
    #    url = self.api_root + '/surveys/' + survey_id
    #    # http method
    #    method = 'GET'
    #    # make request
    #    response = self.fetch(url, method=method)
    #    # test response
    #    self.assertTrue(response.code == 401)

    def test_get_single_survey_with_specific_fields(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to tests
        url = self.api_root + '/surveys/' + survey_id
        query_params = {
            'fields': 'title,creator_name'
        }
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json_decode(response.body)
        self.assertEqual(
            survey_dict,
            OrderedDict((
                ('title', OrderedDict((('English', 'single_survey'),))),
                ('creator_name', 'test_user'),
            ))
        )

    def test_surveys_dont_have_a_type_constraint(self):
        # url to tests
        url = self.api_root + '/surveys'
        query_params = {
            'type': 'integer',
        }
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        self.assertEqual(response.code, 400)
        self.assertIn('has no attribute', json_decode(response.body)['error'])

    def test_list_surveys_with_specific_fields(self):
        # url to tests
        url = self.api_root + '/surveys'
        query_params = {
            'fields': 'deleted,creator_name',
            'limit': 2,
        }
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json.loads(
            response.body.decode(), object_pairs_hook=OrderedDict
        )
        self.assertEqual(
            survey_dict,
            OrderedDict((
                (
                    'surveys',
                    [
                        OrderedDict((
                            ('deleted', False), ('creator_name', 'test_user'))
                        ),
                        OrderedDict((
                            ('deleted', False), ('creator_name', 'test_user'))
                        ),
                    ],
                ),
                ('total_entries', 14),
                ('filtered_entries', 14),
                ('fields', 'deleted,creator_name'),
                ('limit', 2),
            )),
            msg=survey_dict
        )

    def test_list_surveys_with_specific_fields_and_filter(self):
        # url to tests
        url = self.api_root + '/surveys'
        query_params = OrderedDict((
            ('fields', 'deleted,creator_name'),
            ('search', 'a'),
        ))
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json.loads(
            response.body.decode(), object_pairs_hook=OrderedDict
        )
        self.assertEqual(len(survey_dict['surveys']), 6)
        self.assertEqual(survey_dict['total_entries'], 14)
        self.assertEqual(survey_dict['filtered_entries'], 6)

    def test_list_surveys_with_specific_fields_and_filter_and_limit(self):
        # url to tests
        url = self.api_root + '/surveys'
        query_params = OrderedDict((
            ('fields', 'deleted,creator_name'),
            ('search', 'a'),
            ('limit', 2),
        ))
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        survey_dict = json.loads(
            response.body.decode(), object_pairs_hook=OrderedDict
        )
        self.assertEqual(
            survey_dict,
            OrderedDict((
                (
                    'surveys',
                    [
                        OrderedDict((
                            ('deleted', False), ('creator_name', 'test_user'))
                        ),
                        OrderedDict((
                            ('deleted', False), ('creator_name', 'test_user'))
                        ),
                    ],
                ),
                ('total_entries', 14),
                ('filtered_entries', 6),
                ('fields', 'deleted,creator_name'),
                ('limit', 2),
                ('search', 'a'),
            )),
            msg=survey_dict
        )


class TestSubmissionApi(DokoHTTPTest):
    def test_list_submissions(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # check that response is valid parseable json
        submission_dict = json_decode(response.body)

        # check that the expected keys are present
        self.assertTrue('submissions' in submission_dict)
        self.assertEqual(
            len(submission_dict['submissions']), TOTAL_SUBMISSIONS)

        self.assertFalse("error" in submission_dict)

    def test_list_submissions_search_submitter_name(self):
        search_term = 'singular'
        # url to test
        url = self.api_root + '/submissions'
        query_params = {
            'search': search_term,
            'search_fields': 'submitter_name'
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('submissions', response_body, msg=response_body)
        submissions = response_body['submissions']

        self.assertEqual(len(submissions), 1)

    def test_list_submissions_search_submitter_name_regex(self):
        search_term = '.*singular'
        # url to test
        url = self.api_root + '/submissions'
        query_params = {
            'search': search_term,
            'search_fields': 'submitter_name',
            'regex': 'true',
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('submissions', response_body, msg=response_body)
        submissions = response_body['submissions']

        self.assertEqual(len(submissions), 1)

    def test_get_single_submission(self):
        submission_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/submissions/' + submission_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertFalse("error" in submission_dict)

    def test_create_public_submission(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)
        self.assertEqual(
            submission_dict['enumerator_user_id'],
            'b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
        )

    def test_create_public_submission_alternate_url(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)
        self.assertEqual(
            submission_dict['enumerator_user_id'],
            'b7becd02-1a3f-4c1d-a0e1-286ba121aef4'
        )

    def test_create_public_submission_not_logged_in(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(
            url, method=method, body=json_encode(body), _logged_in_user=None
        )
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertIn('save_time', submission_dict, msg=submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)
        self.assertNotIn('enumerator_user_id', submission_dict)

    def test_create_public_submission_not_logged_in_alternate_url(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(
            url, method=method, body=json_encode(body), _logged_in_user=None
        )
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertIn('save_time', submission_dict, msg=submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)
        self.assertNotIn('enumerator_user_id', submission_dict)

    def test_create_public_submission_no_survey_id(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, response.body)

        submission_dict = json_decode(response.body)
        self.assertIn('property is required', submission_dict['error'])

    def test_create_public_submission_survey_does_not_exist(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            'survey_id': str(uuid.uuid4()),
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400)

        submission_dict = json_decode(response.body)
        self.assertIn('could not be found', submission_dict['error'])

    def test_submit_public_survey_does_not_exist_alternate_url(self):
        survey_id = str(uuid.uuid4())
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 404)

    def test_create_public_submission_with_no_survey_node_id(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "type_constraint": "integer",
                    "answer": 3,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400)

        submission_dict = json_decode(response.body)
        self.assertIn('property is required', submission_dict['error'])

    def test_submit_public_no_survey_node_id_alternate_url(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "type_constraint": "integer",
                    "answer": 3,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400)

        submission_dict = json_decode(response.body)
        self.assertIn('property is required', submission_dict['error'])

    def test_create_public_submission_with_bogus_survey_node_id(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    'survey_node_id': str(uuid.uuid4()),
                    "type_constraint": "integer",
                    "answer": 3,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400)

        submission_dict = json_decode(response.body)
        self.assertIn('survey_node not found', submission_dict['error'])

    def test_submit_public_with_bogus_survey_node_id_alternate_url(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    'survey_node_id': str(uuid.uuid4()),
                    "type_constraint": "integer",
                    "answer": 3,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400)

        submission_dict = json_decode(response.body)
        self.assertIn('survey_node not found', submission_dict['error'])

    def test_create_public_submission_with_integer_answer(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "60e56824-910c-47aa-b5c0-71493277b43f",
                    "type_constraint": "integer",
                    "answer": 3
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertEqual(len(submission_dict['answers']), 1)

        self.assertEqual(
            submission_dict['answers'][0]['response'],
            3
        )

    def test_cannot_skip_first_required_question_no_sub_surveys(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'first question required'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                        ),
                        models.construct_survey_node(
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'optional second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'first question required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'text',
                    "answer": 'oops I skipped it',
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('skipped', json_decode(response.body)['error'])

    def test_legitimate_question_skip(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'first question required'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                        ),
                        models.construct_survey_node(
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'optional second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'first question required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 3,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_cannot_skip_second_required_question_no_sub_surveys(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'second question required'},
                    nodes=[
                        models.construct_survey_node(
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'optional first'},
                            ),
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'required second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'second question required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 999,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('skipped', json_decode(response.body)['error'])

    def test_must_answer_both_required_questions(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'two required questions'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'required second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'two required questions'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 999,
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('skipped', json_decode(response.body)['error'])

    def test_cannot_skip_sub_survey(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'sub surveys now'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[0, 5]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            required=True,
                                            node=models.construct_node(
                                                type_constraint='integer',
                                                title={'English': 'a'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            required=True,
                                            node=models.construct_node(
                                                type_constraint='integer',
                                                title={'English': 'b'},
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'optional second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'sub surveys now'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 2,
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'text',
                    "answer": 'did I skip something?',
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('skipped', json_decode(response.body)['error'])

    def test_can_skip_sub_survey_outside_bucket(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'sub surveys outside bucket'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[0, 5]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            required=True,
                                            node=models.construct_node(
                                                type_constraint='integer',
                                                title={'English': 'a'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            required=True,
                                            node=models.construct_node(
                                                type_constraint='integer',
                                                title={'English': 'b'},
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'required second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'sub surveys outside bucket'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 7,
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'text',
                    "answer": 'did not skip',
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_required_questions_with_sub_surveys(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'sub surveys outside bucket'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'required first'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[0, 5]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            node=models.construct_node(
                                                type_constraint='note',
                                                title={'English': 'a'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            required=True,
                                            node=models.construct_node(
                                                type_constraint='integer',
                                                title={'English': 'b'},
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='text',
                                title={'English': 'required second'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)
        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'sub surveys outside bucket'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 3,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 3,
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'text',
                    "answer": 'did not skip',
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_can_skip_sub_survey_not_traversed(self):
        survey_url = self.api_root + '/surveys'
        body = {
            'survey_type': 'public',
            'title': {'English': 'skip non traversed'},
            'nodes': [
                {
                    'required': True,
                    'node': {
                        'title': {'English': 'a'},
                        'type_constraint': 'integer',
                    },
                    'sub_surveys': [
                        {
                            'nodes': [
                                {
                                    'required': True,
                                    'node': {
                                        'type_constraint': 'integer',
                                        'title': {
                                            'English': 'b',
                                        },
                                    },
                                },
                                {
                                    'required': True,
                                    'node': {
                                        'type_constraint': 'integer',
                                        'title': {
                                            'English': 'c',
                                        },
                                    },
                                },
                            ],
                            'buckets': [
                                {
                                    'bucket_type': 'integer',
                                    'bucket': '[0, 5]',
                                },
                            ],
                        },
                        {
                            'nodes': [
                                {
                                    'required': True,
                                    'node': {
                                        'type_constraint': 'integer',
                                        'title': {
                                            'English': 'e',
                                        },
                                    },
                                },
                                {
                                    'required': True,
                                    'node': {
                                        'type_constraint': 'integer',
                                        'title': {
                                            'English': 'f',
                                        },
                                    },
                                },
                            ],
                            'buckets': [
                                {
                                    'bucket_type': 'integer',
                                    'bucket': '[7, 10]',
                                },
                            ],
                        },
                    ],
                },
                {
                    'required': True,
                    'node': {
                        'title': {'English': 'd'},
                        'type_constraint': 'text',
                    },
                },
            ],
        }
        survey_response = self.fetch(
            survey_url, method='POST', body=json_encode(body)
        )
        self.assertEqual(survey_response.code, 201, msg=survey_response.body)

        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'skip non traversed'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 3,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 3,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 3,
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'text',
                    "answer": 'did not skip',
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_repeatable_required_valid(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'repeatable required'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'how many?'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    repeatable=True,
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[,]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            repeatable=True,
                                            required=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='integer',
                                                title={'English': 'age?'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            repeatable=True,
                                            required=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='text',
                                                title={'English': 'name?'},
                                            ),
                                        ),
                                    ],
                                )
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'something else'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)

        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'repeatable required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 2,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 20,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'text',
                    "answer": 'Person',
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 30,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'text',
                    "answer": 'Other Person',
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'integer',
                    "answer": 12,
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_repeatable_required_not_enough_responses(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'repeatable required'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'how many?'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    repeatable=True,
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[,]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            repeatable=True,
                                            required=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='integer',
                                                title={'English': 'age?'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            repeatable=True,
                                            required=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='text',
                                                title={'English': 'name?'},
                                            ),
                                        ),
                                    ],
                                )
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'something else'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)

        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'repeatable required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 2,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 20,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'text',
                    "answer": 'Person',
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'integer',
                    "answer": 12,
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 400, msg=response.body)
        self.assertIn('skipped', json_decode(response.body)['error'])

    def test_repeatable_required_valid_with_optional_subquestion(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.surveys.append(
                models.construct_survey(
                    survey_type='public',
                    title={'English': 'repeatable required'},
                    nodes=[
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'how many?'},
                            ),
                            sub_surveys=[
                                models.SubSurvey(
                                    repeatable=True,
                                    buckets=[
                                        models.construct_bucket(
                                            bucket_type='integer',
                                            bucket='[,]',
                                        ),
                                    ],
                                    nodes=[
                                        models.construct_survey_node(
                                            repeatable=True,
                                            required=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='integer',
                                                title={'English': 'age?'},
                                            ),
                                        ),
                                        models.construct_survey_node(
                                            repeatable=True,
                                            node=models.construct_node(
                                                allow_multiple=True,
                                                type_constraint='text',
                                                title={'English': 'name?'},
                                            ),
                                        ),
                                    ],
                                )
                            ],
                        ),
                        models.construct_survey_node(
                            required=True,
                            node=models.construct_node(
                                type_constraint='integer',
                                title={'English': 'something else'},
                            ),
                        ),
                    ],
                )
            )
            self.session.add(user)

        survey = (
            self.session
            .query(Survey)
            .filter(
                Survey.title['English'].astext == 'repeatable required'
            )
            .one()
        )

        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": survey.id,
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": survey.nodes[0].id,
                    "type_constraint": 'integer',
                    "answer": 2,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 20,
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[1].id
                    ),
                    "type_constraint": 'text',
                    "answer": 'Person',
                },
                {
                    "survey_node_id": (
                        survey.nodes[0].sub_surveys[0].nodes[0].id
                    ),
                    "type_constraint": 'integer',
                    "answer": 30,
                },
                {
                    "survey_node_id": survey.nodes[1].id,
                    "type_constraint": 'integer',
                    "answer": 12,
                },
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201, msg=response.body)

    def test_create_public_submission_with_integer_answer_alternate_url(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "submitter_name": "regular",
            "submission_type": "unauthenticated",
            "answers": [
                {
                    "survey_node_id": "60e56824-910c-47aa-b5c0-71493277b43f",
                    "type_constraint": "integer",
                    "answer": 3
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

        self.assertEqual(len(submission_dict['answers']), 1)

        self.assertEqual(
            submission_dict['answers'][0]['response'],
            3
        )

    def test_create_enum_only_submission(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "c0816b52-204f-41d4-aaf0-ac6ae2970925",
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
            "submission_type": "authenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    def test_create_enum_only_submission_alternate_url(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
            "submission_type": "authenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertIn('save_time', submission_dict, msg=submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    def test_cannot_create_enumerator_only_submission_not_logged_in(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "c0816b52-204f-41d4-aaf0-ac6ae2970925",
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
        }
        # make request
        response = self.fetch(
            url, method=method, body=json_encode(body), _logged_in_user=None
        )
        self.assertEqual(response.code, 401, msg=response.body)

    def test_401_enumerator_only_submission_not_logged_in_alternate_url(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
        }
        # make request
        response = self.fetch(
            url, method=method, body=json_encode(body), _logged_in_user=None
        )
        self.assertEqual(response.code, 401, msg=response.body)

    def test_submission_defaults_to_authenticated(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "c0816b52-204f-41d4-aaf0-ac6ae2970925",
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    def test_submission_defaults_to_authenticated_alternate_url(self):
        survey_id = 'c0816b52-204f-41d4-aaf0-ac6ae2970925'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = {
            "enumerator_user_id": "a7becd02-1a3f-4c1d-a0e1-286ba121aef3",
            "submitter_name": "regular",
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))
        self.assertEqual(response.code, 201)

        submission_dict = json_decode(response.body)

        self.assertTrue('save_time' in submission_dict)
        self.assertTrue('deleted' in submission_dict)
        self.assertTrue('id' in submission_dict)
        self.assertTrue('submitter_email' in submission_dict)
        self.assertTrue('answers' in submission_dict)
        self.assertTrue('submitter_name' in submission_dict)
        self.assertTrue('last_update_time' in submission_dict)
        self.assertTrue('submission_time' in submission_dict)
        self.assertTrue('survey_id' in submission_dict)

    # TODO: This was deemed unnecessary, submissions should be created
    # one at a time.
    # def test_create_multiple_submissions(self):
    #    # url to test
    #    url = self.api_root + '/submissions/batch'
    #    # http method
    #    method = 'POST'
    #    # body
    #    body = '{"submission_body_json"}'
    #    # make request
    #    response = self.fetch(url, method=method, body=body)
    #    # test response
    #    self.fail("Not yet implemented.")

    def test_delete_submission(self):
        submission_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/submissions/' + submission_id
        # http method
        method = 'DELETE'
        # make request
        response = self.fetch(url, method=method)
        # test response - successful DELETE returns 204 no content.
        self.assertEqual(response.code, 204)

        submission = self.session.query(Submission).get(submission_id)

        self.assertTrue(submission.deleted)


class TestNodeApi(DokoHTTPTest):
    def test_list_nodes(self):
        # url to test
        url = self.api_root + '/nodes'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        node_dict = json_decode(response.body)
        # check that the expected keys are present
        self.assertIn('nodes', node_dict, msg=node_dict)

        self.assertEqual(len(node_dict['nodes']), TOTAL_NODES)

        # check that no error is present
        self.assertFalse("error" in node_dict)

    def test_list_nodes_with_limit(self):
        limit = 1
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'limit': limit
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response

        node_dict = json_decode(response.body)

        self.assertIn('nodes', node_dict, msg=node_dict)
        self.assertTrue('limit' in node_dict)
        self.assertEqual(node_dict['limit'], limit)
        self.assertEqual(len(node_dict['nodes']), limit)

        # check that no error is present
        self.assertFalse("error" in node_dict)

    def test_list_nodes_with_offset(self):
        offset = 5
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'offset': offset
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        node_dict = json_decode(response.body)

        self.assertTrue('nodes' in node_dict)
        self.assertTrue('offset' in node_dict)
        self.assertEqual(node_dict['offset'], offset)
        self.assertEqual(len(node_dict['nodes']), TOTAL_NODES - offset)

        # check that no error is present
        self.assertFalse("error" in node_dict)

    def test_list_nodes_with_title_search(self):
        search_term = 'integer'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title'
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 3)
        self.assertListEqual(
            ['integer' in nodes[i]['title']['English'] for i in range(3)],
            [True] * 3,
            msg="Some of the returned titles don't contain the search term."
        )

    def test_list_nodes_none_matching(self):
        search_term = 'not going to find this'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title'
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 0, msg=nodes)
        self.assertEqual(response_body['filtered_entries'], 0)

    def test_list_nodes_order_by_title(self):
        with self.session.begin():
            self.session.add_all((
                models.construct_node(
                    languages=['French'],
                    title={'French': 'ccc'},
                    hint={'French': ''},
                    type_constraint='integer',
                ),
                models.construct_node(
                    languages=['German', 'French'],
                    title={
                        'French': 'bbb',
                        'German': 'aaa',
                    },
                    hint={'German': '', 'French': ''},
                    type_constraint='decimal',
                ),
            ))

        search_term = '...'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title',
            'regex': 'true',
            'lang': 'French',
            'order_by': "title->>'French':ASC",
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['title']['French'], 'bbb')
        self.assertEqual(nodes[1]['title']['French'], 'ccc')

    def test_list_nodes_with_title_and_language_search(self):
        with self.session.begin():
            self.session.add_all((
                models.construct_node(
                    languages=['French'],
                    title={'French': 'integer'},
                    hint={'French': ''},
                    type_constraint='integer',
                ),
                models.construct_node(
                    languages=['French'],
                    title={'French': 'decimal'},
                    hint={'French': ''},
                    type_constraint='decimal',
                ),
            ))

        search_term = 'integer'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title',
            'lang': 'French',
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['title'], {'French': 'integer'})

    def test_list_nodes_with_regex_search(self):
        with self.session.begin():
            self.session.add_all((
                models.construct_node(
                    languages=['French'],
                    title={'French': '345'},
                    hint={'French': ''},
                    type_constraint='integer',
                ),
                models.construct_node(
                    languages=['German'],
                    title={'German': '678'},
                    hint={'German': ''},
                    type_constraint='decimal',
                ),
            ))

        search_term = '\d+'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title',
            'regex': 'true',
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]['title'], {'French': '345'})
        self.assertEqual(nodes[1]['title'], {'German': '678'})

    def test_list_nodes_with_regex_and_language_search(self):
        with self.session.begin():
            self.session.add_all((
                models.construct_node(
                    languages=['French'],
                    title={'French': '345'},
                    hint={'French': ''},
                    type_constraint='integer',
                ),
                models.construct_node(
                    languages=['German'],
                    title={'German': '678'},
                    hint={'German': ''},
                    type_constraint='decimal',
                ),
            ))

        search_term = '\d+'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'search': search_term,
            'search_fields': 'title',
            'regex': 'true',
            'lang': 'French',
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        response_body = json_decode(response.body)
        self.assertIn('nodes', response_body, msg=response_body)
        nodes = response_body['nodes']

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['title'], {'French': '345'})

    def test_list_nodes_with_type_filter(self):
        type_constraint = 'text'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'type': type_constraint
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        node_dict = json_decode(response.body)

        self.assertTrue('nodes' in node_dict)
        self.assertTrue('type' in node_dict)
        self.assertEqual(len(node_dict['nodes']), 1)
        self.assertEqual(
            node_dict['nodes'][0]['type_constraint'], type_constraint)

    def test_list_nodes_with_unknown_type_filter(self):
        type_constraint = 'wrong'
        # url to test
        url = self.api_root + '/nodes'
        query_params = {
            'type': type_constraint
        }
        # append query params
        url = self.append_query_params(url, query_params)
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        node_dict = json_decode(response.body)

        self.assertEqual(response.code, 400)
        self.assertTrue('error' in node_dict)

    def test_get_single_node(self):
        node_id = '60e56824-910c-47aa-b5c0-71493277b43f'
        # url to test
        url = self.api_root + '/nodes/' + node_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertIn('id', node_dict, msg=node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertFalse("error" in node_dict)

    def test_create_note_node(self):
        type_constraint = 'note'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": "test_time_node"},
            "type_constraint": type_constraint,
            "logic": {}
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_text_node(self):
        type_constraint = 'text'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_photo_node(self):
        type_constraint = 'text'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_integer_node(self):
        type_constraint = 'integer'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_decimal_node(self):
        type_constraint = 'decimal'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_date_node(self):
        type_constraint = 'date'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_time_node(self):
        type_constraint = 'time'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_timestamp_node(self):
        type_constraint = 'timestamp'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_location_node(self):
        type_constraint = 'location'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_facility_node(self):
        type_constraint = 'facility'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_create_multiple_choice_node(self):
        type_constraint = 'multiple_choice'
        # url to test
        url = self.api_root + '/nodes'
        # http method
        method = 'POST'
        # body
        body = {
            "title": {"English": type_constraint + "_node"},
            "hint": {
                "English": "Some test hint."
            },
            "allow_multiple": False,
            "allow_other": False,
            "type_constraint": type_constraint,
            "logic": {},
            "choices": [
                {
                    "choice_text": {
                        "English": "first choice"
                    }
                },
                {
                    "choice_text": {
                        "English": "second choice"
                    }
                }
            ]
        }

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        self.assertEqual(response.code, 201)

        # test response
        # check that response is valid parseable json
        node_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in node_dict)
        self.assertTrue('title' in node_dict)
        self.assertTrue('hint' in node_dict)
        self.assertTrue('allow_multiple' in node_dict)
        self.assertTrue('allow_other' in node_dict)
        self.assertTrue('logic' in node_dict)
        self.assertTrue('last_update_time' in node_dict)
        self.assertTrue('type_constraint' in node_dict)
        self.assertTrue('choices' in node_dict)
        self.assertEqual(len(node_dict['choices']), 2)

        self.assertEqual(node_dict['type_constraint'], type_constraint)

        self.assertFalse("error" in node_dict)

    def test_update_node(self):
        node_id = '60e56824-910c-47aa-b5c0-71493277b43f'
        self.assertFalse(
            self.session.query(Node.deleted).filter_by(id=node_id).scalar()
        )
        # url to test
        url = self.api_root + '/nodes/' + node_id
        # http method
        method = 'PUT'
        # body
        body = {
            'deleted': True
        }
        encoded_body = json_encode(body)
        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        # test response
        self.assertTrue(json_decode(response.body)['deleted'])
        self.assertTrue(
            self.session.query(Node.deleted).filter_by(id=node_id).scalar()
        )

    def test_update_node_not_found(self):
        node_id = str(uuid.uuid4())
        # url to test
        url = self.api_root + '/nodes/' + node_id
        # http method
        method = 'PUT'
        # body
        body = {
            'deleted': True
        }
        encoded_body = json_encode(body)
        # make request
        response = self.fetch(url, method=method, body=encoded_body)
        # test response
        self.assertEqual(response.code, 404)
        self.assertEqual(
            json_decode(response.body)['error'],
            'Resource not found.'
        )

    def test_delete_node(self):
        node_id = '60e56824-910c-47aa-b5c0-71493277b43f'
        # url to test
        url = self.api_root + '/nodes/' + node_id
        # http method
        method = 'DELETE'
        # make request
        response = self.fetch(url, method=method)
        # test response
        # test response - successful DELETE returns 204 no content.
        self.assertEqual(response.code, 204)

        survey = self.session.query(Node).get(node_id)

        self.assertTrue(survey.deleted)

    def test_delete_node_not_found(self):
        node_id = str(uuid.uuid4())
        # url to test
        url = self.api_root + '/nodes/' + node_id
        # http method
        method = 'DELETE'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.assertEqual(response.code, 404)
        self.assertEqual(
            json_decode(response.body)['error'],
            'Resource not found.'
        )

    def test_list_nodes_including_deleted(self):
        node_id = '60e56824-910c-47aa-b5c0-71493277b43f'
        delete_url = self.api_root + '/nodes/' + node_id
        self.fetch(delete_url, method='DELETE')

        list_url = self.api_root + '/nodes'
        regular_response = self.fetch(list_url, method='GET')
        self.assertEqual(
            len(json_decode(regular_response.body)['nodes']),
            TOTAL_NODES - 1
        )

        list_deleted_url = self.append_query_params(
            list_url, {'show_deleted': 'true'}
        )
        include_deleted_response = self.fetch(list_deleted_url, method='GET')
        self.assertEqual(
            len(json_decode(include_deleted_response.body)['nodes']),
            TOTAL_NODES
        )


class TestUserApi(DokoHTTPTest):
    def test_create_api_token(self):
        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        self.assertIsNone(user.token)
        # url to test
        url = self.api_root + '/user/generate-api-token'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        response_dict = json_decode(response.body)
        # test response
        token = response_dict['token']
        expiration = response_dict['expires_on']
        self.assertTrue(bcrypt_sha256.verify(token, user.token))
        self.assertEqual(expiration, user.token_expiration.isoformat())
        self.assertEqual(
            dateutil.parser.parse(expiration).date(),
            (datetime.now() + timedelta(days=60)).date()
        )

    def test_use_api_token(self):
        # url to test
        url = self.api_root + '/user/generate-api-token'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        token = json_decode(response.body)['token']

        api_url = self.api_root + '/nodes'
        api_response = self.fetch(
            api_url, method='GET', _logged_in_user=None,
            headers={'Email': 'test_creator@fixtures.com', 'Token': token},
        )
        self.assertEqual(
            api_response.body, self.fetch(api_url, method='GET').body
        )

    def test_use_wrong_api_token(self):
        api_url = self.api_root + '/nodes'
        api_response = self.fetch(
            api_url, method='GET', _logged_in_user=None,
            headers={'Email': 'test_creator@fixtures.com', 'Token': 'wrong'},
        )

        self.assertEqual(api_response.code, 401)

    def test_use_expired_api_token(self):
        # url to test
        url = self.api_root + '/user/generate-api-token'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        token = json_decode(response.body)['token']

        user = (
            self.session
            .query(SurveyCreator)
            .get('b7becd02-1a3f-4c1d-a0e1-286ba121aef4')
        )
        with self.session.begin():
            user.token_expiration = datetime.now() - timedelta(days=1)

        api_url = self.api_root + '/nodes'
        api_response = self.fetch(
            api_url, method='GET', _logged_in_user=None,
            headers={'Email': 'test_creator@fixtures.com', 'Token': token},
        )

        self.assertEqual(api_response.code, 401)
