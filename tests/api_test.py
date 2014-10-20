"""
Tests for the dokomo JSON api

"""
import json
import unittest

from sqlalchemy import and_

import api.survey
import api.submission
from db.logical_constraint import logical_constraint_table
from db.question import question_table
from db.submission import submission_table
from db.survey import survey_table


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


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        survey_table.delete().where(
            survey_table.c.title == 'view title').execute()
        column = logical_constraint_table.c.logical_constraint_name
        logical_constraint_table.delete().where(
            column == 'does not exist').execute()

    def testGetOne(self):
        survey_id = survey_table.select().execute().first().survey_id
        data = api.survey.get_one({'survey_id': survey_id})
        self.assertIsNotNone(data['survey_id'])
        self.assertIsNotNone(data['questions'])

    def testGetMany(self):
        surveys = api.survey.get_many()
        self.assertGreater(len(surveys), 0)

    def testCreate(self):
        questions = [{'title': 'view question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logical_constraint_name': 'does not exist'}]
        data = {'title': 'view title',
                'questions': questions}
        survey_id = api.survey.create(data)['survey_id']
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 1)


if __name__ == '__main__':
    unittest.main()

