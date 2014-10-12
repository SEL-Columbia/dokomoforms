"""
Tests for the dokomo database

"""
import unittest

from db.answer import answer_insert, answer_table
from db.question import get_questions
from db.submission import submission_insert, submission_table
from db.survey import survey_table


class TestAnswer(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testInsertAnswerAndDelete(self):
        survey_id = survey_table.select().execute().first().survey_id
        question_id = get_questions(survey_id).first().question_id
        submission_exec = submission_insert(latitude=0, longitude=0,
                                            submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = answer_insert(answer=1, question_id=question_id,
                                    submission_id=submission_id,
                                    survey_id=survey_id).execute()
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)
        condition = answer_table.c.answer_id == answer_id
        answer_table.delete().where(condition).execute()
        self.assertEqual(
            answer_table.select().where(condition).execute().rowcount, 0)


if __name__ == '__main__':
    unittest.main()

