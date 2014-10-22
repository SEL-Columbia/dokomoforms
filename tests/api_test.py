"""
Tests for the dokomo JSON api

"""
import json
import unittest

from sqlalchemy import and_

import api.survey
import api.submission
from db.answer import answer_insert
from db.question import question_table, get_questions
from db.submission import submission_table, submission_insert, \
    SubmissionDoesNotExistError, submission_select
from db.survey import survey_table, survey_select, SurveyDoesNotExistError


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testSubmit(self):
        survey_id = survey_table.select().execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        data = {'survey_id': survey_id,
                'answers': [{'question_id': question_id, 'answer': 1}]}
        submission_id = api.submission.submit(data)['submission_id']
        condition = submission_table.c.submission_id == submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)

    def testGet(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'location')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_insert(answer=[90, 0], question_id=question_id,
                      submission_id=submission_id,
                      survey_id=survey_id).execute()
        data = api.submission.get(submission_id)
        self.assertIsNotNone(data['submission_id'])
        self.assertIsNotNone(data['answers'])

    def testGetForSurvey(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question_id = q_where.execute().first().question_id
        for i in range(2):
            submission_exec = submission_insert(submitter='test_submitter',
                                                survey_id=survey_id).execute()
            submission_id = submission_exec.inserted_primary_key[0]
            answer_insert(answer=i, question_id=question_id,
                          submission_id=submission_id,
                          survey_id=survey_id).execute()
        data = api.submission.get_for_survey(survey_id)
        self.assertGreater(len(data), 0)

    def testDelete(self):
        survey_id = survey_table.select().execute().first().survey_id
        data = {'survey_id': survey_id,
                'answers': [{'answer': None}]}
        submission_id = api.submission.submit(data)['submission_id']
        api.submission.delete(submission_id)
        self.assertRaises(SubmissionDoesNotExistError, submission_select,
                          submission_id)


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        survey_table.delete().where(
            survey_table.c.title != 'test_title').execute()

    def testGetOne(self):
        survey_id = survey_table.select().execute().first().survey_id
        data = api.survey.get_one(survey_id)
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])

    def testGetMany(self):
        surveys = api.survey.get_many()
        self.assertGreater(len(surveys), 0)

    def testCreate(self):
        questions = [{'title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': {'min': 3}}]
        data = {'title': 'api_test survey',
                'questions': questions}
        survey_id = api.survey.create(data)['survey_id']
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 1)
        self.assertEqual(get_questions(survey_id).first().logic, {'min': 3})

    def testUpdate(self):
        questions = [{'title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None}]
        data = {'title': 'api_test survey',
                'questions': questions}
        survey_id = api.survey.create(data)['survey_id']
        question_id = get_questions(survey_id).first().question_id

        update_json = {'survey_id': survey_id,
                       'title': 'updated survey title'}
        questions = [{'question_id': question_id,
                      'title': 'updated question title'},
                     {'title': 'second question',
                      'type_constraint_name': 'integer',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None}]
        update_json['questions'] = questions
        api.survey.update(update_json)
        upd_survey = survey_select(survey_id)
        upd_questions = list(get_questions(survey_id))
        self.assertEqual(upd_survey.title, 'updated survey title')
        self.assertEqual(upd_questions[0].title, 'updated question title')
        self.assertEqual(upd_questions[1].title, 'second question')

    def testDelete(self):
        data = {'title': 'api_test survey'}
        survey_id = api.survey.create(data)['survey_id']
        api.survey.delete(survey_id)
        self.assertRaises(SurveyDoesNotExistError, survey_select, survey_id)


if __name__ == '__main__':
    unittest.main()

