"""API tests"""

from tornado.escape import json_decode, json_encode

from tests.util import DokoHTTPTest, setUpModule, tearDownModule

utils = (setUpModule, tearDownModule)


"""
TODO: add expception and error response tests
"""


class TestSurveyApi(DokoHTTPTest):

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

        self.assertTrue(len(survey_dict['surveys']) == 11)

        # check that no error is present
        self.assertFalse("error" in survey_dict)

    def test_list_surveys_with_offset(self):
        # url to test
        url = self.api_root + '/surveys'
        query_params = {
            'offset': 5
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
        self.assertEqual(survey_dict['offset'], 5)

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

    def test_get_single_survey(self):
        survey_id = 'b0816b52-204f-41d4-aaf0-ac6ae2970923'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response

        # check that response is valid parseable json
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('survey_id' in survey_dict)
        self.assertTrue('survey_metadata' in survey_dict)
        self.assertTrue('questions' in survey_dict)
        self.assertTrue('survey_title' in survey_dict)
        self.assertTrue('survey_version' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('last_updated' in survey_dict)

    def test_create_survey(self):
        # login - user has been created in fixtures
        self.login('test_user')

        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "enumerator_only": "false",
            "deleted": False,
            "translations": {},
            "default_language": "English",
            "title": "Another Test Survey",
            "nodes": [
                {
                    "title": "time_node",
                    "hint": {
                        "English": ""
                    },
                    "allow_multiple": False,
                    "allow_other": False,
                    "type_constraint": "time",
                    "logic": {},
                    "deleted": False
                }
            ]
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))

        print(response)

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

    def test_update_survey(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method
        method = 'PUT'
        # body
        body = '{"survey_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")

    def test_delete_survey(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method
        method = 'DELETE'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_delete_survey_via_post(self):
        survey_id = 'A known id'
        query_params = {
            '_method': 'DELETE'
        }
        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # append query params
        url = self.append_query_params(url, query_params)
        # http method
        method = 'POST'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_submit_to_survey(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submit'
        # http method
        method = 'POST'
        # body
        body = '{"submission_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")

    def test_list_submissions_to_survey(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/submissions'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_get_stats_for_survey(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/stats'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_submission_activity_for_all_surveys(self):
        # url to test
        url = self.api_root + '/surveys/activity'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_submission_activity_for_single_surveys(self):
        survey_id = 'A known id'
        # url to test
        url = self.api_root + '/surveys/' + survey_id + '/activity'
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_survey_access_denied_for_unauthorized_user(self):
        survey_id = 'A known id'

        # TODO: Logout -+

        # url to test
        url = self.api_root + '/surveys/' + survey_id
        # http method
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")


class TestSubmissionApi(DokoHTTPTest):

    def test_list_submission(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_get_single_submission(self):
        submission_id = 'A known id'
        # url to test
        url = self.api_root + '/submissions/' + submission_id
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_create_submission(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = '{"submission_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")

    def test_create_multiple_submissions(self):
        # url to test
        url = self.api_root + '/submissions/batch'
        # http method
        method = 'POST'
        # body
        body = '{"submission_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")

    def test_delete_submission(self):
        submission_id = 'A known id'
        # url to test
        url = self.api_root + '/submissions/' + submission_id
        # http method
        method = 'DELETE'
        # body
        body = '{"submission_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")

    def test_delete_submission_via_post(self):
        submission_id = 'A known id'
        query_params = {
            '_method': 'DELETE'
        }
        # url to test
        url = self.api_root + '/submissions/' + submission_id
        # append query params
        url = self.append_query_params(url, query_params)
        # http method
        method = 'POST'
        # body
        body = '{"submission_body_json"}'
        # make request
        response = self.fetch(url, method=method, body=body)
        # test response
        self.fail("Not yet implemented.")


class TestUserApi(DokoHTTPTest):

    def test_create_api_token(self):
        # url to test
        url = self.api_root + '/user/generate-api-token'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")

    def test_use_api_token(self):
        # url to test
        url = self.api_root + '/user/generate-api-token'
        # http method (just for clarity)
        method = 'GET'
        # make request
        response = self.fetch(url, method=method)
        # test response
        self.fail("Not yet implemented.")
