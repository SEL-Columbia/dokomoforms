"""
Tests for the dokomo database

"""
import unittest
import json
from sqlalchemy import and_
from db.question import question_table

from views.submission import submit

from db.submission import submission_table
from db.survey import survey_table
from views.survey import create


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
        submission_id = submit(data)
        condition = submission_table.c.submission_id == submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        survey_table.delete().where(
            survey_table.c.title == 'view title').execute()

    def testCreate(self):
        questions = [{'title': 'view question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logical_constraint_name': None}]
        data = {'title': 'view title',
                'questions': questions}
        survey_id = create(data)
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 1)


if __name__ == '__main__':
    unittest.main()

