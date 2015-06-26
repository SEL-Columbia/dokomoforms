"""API tests"""
from tornado.escape import json_decode, json_encode

from tests.util import DokoHTTPTest, setUpModule, tearDownModule

from dokomoforms.models import Submission, Survey

utils = (setUpModule, tearDownModule)


"""
TODO: add expception and error response tests
"""

# The numbers expected to be present via fixtures
TOTAL_SURVEYS = 14
TOTAL_SUBMISSIONS = 112


class TestSurveyApi(DokoHTTPTest):
    """
    These tests are made against the known fixture data.
    """

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
        self.assertEqual(int(survey_dict['offset']), offset)

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
        self.assertEqual(int(survey_dict['limit']), 1)

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
        survey_dict = json_decode(response.body)

        # check that expected keys are present
        self.assertTrue('id' in survey_dict)
        self.assertTrue('created_on' in survey_dict)
        self.assertTrue('metadata' in survey_dict)
        self.assertTrue('title' in survey_dict)
        self.assertTrue('enumerator_only' in survey_dict)
        self.assertTrue('default_language' in survey_dict)
        self.assertTrue('deleted' in survey_dict)
        self.assertTrue('creator_name' in survey_dict)
        self.assertTrue('nodes' in survey_dict)
        self.assertTrue('last_update_time' in survey_dict)
        self.assertTrue('creator_id' in survey_dict)
        self.assertTrue('version' in survey_dict)

        self.assertFalse("error" in survey_dict)

    def test_create_survey(self):
        # url to test
        url = self.api_root + '/surveys'
        # http method
        method = 'POST'
        # body
        body = {
            "metadata": {},
            "enumerator_only": "false",
            "deleted": False,
            "default_language": "English",
            "title": {"English": "Test_Survey"},
            "nodes": [
                {
                    "title": {"English": "test_time_node"},
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

        encoded_body = json_encode(body)

        # make request
        response = self.fetch(url, method=method, body=encoded_body)

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
            "survey_id": "b0816b52-204f-41d4-aaf0-ac6ae2970923",
            "submitter_name": "regular",
            "submission_type": "unauthenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))

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

        self.assertTrue('submissions' in submission_list)
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
        self.assertTrue("latest_submission_time" in stats)
        self.assertTrue("created_on" in stats)
        self.assertTrue("earliest_submission_time" in stats)
        self.assertTrue("num_submissions" in stats)
        self.assertFalse("error" in stats)

    def test_submission_activity_for_all_surveys(self):
        # url to test
        url = self.api_root + '/surveys/activity'
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

        self.assertDictEqual(
            submission_dict['answers'][0]['response'],
            {'response_type': 'answer', 'response': 3}
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

    def test_create_enum_only_submission_fails_without_enumerator_id(self):
        # url to test
        url = self.api_root + '/submissions'
        # http method
        method = 'POST'
        # body
        body = {
            "survey_id": "c0816b52-204f-41d4-aaf0-ac6ae2970925",
            "submitter_name": "regular",
            "submission_type": "authenticated"
        }
        # make request
        response = self.fetch(url, method=method, body=json_encode(body))

        submission_dict = json_decode(response.body)

        self.assertTrue('error' in submission_dict)

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
