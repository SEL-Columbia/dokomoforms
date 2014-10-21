"""
Tests for the dokomo database

"""
import json
import unittest

from db import update_record, delete_record
from db.answer import answer_insert, answer_table, get_answers, get_geo_json
from db.answer_choice import answer_choice_insert, get_answer_choices
from db.logical_constraint import logical_constraint_table, \
    logical_constraint_exists, logical_constraint_name_insert
from db.question import get_questions, get_question, question_table, \
    get_free_sequence_number, question_insert
from db.question_branch import get_branches
from db.question_choice import get_choices
from db.submission import submission_table, submission_insert, \
    submission_select, get_submissions
from db.survey import survey_table, survey_insert, survey_select

# TODO: write tests for integrity errors

class TestAnswer(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testInsertAnswer(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = answer_insert(answer=1, question_id=question_id,
                                    submission_id=submission_id,
                                    survey_id=survey_id).execute()
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testInsertLocation(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'location')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = answer_insert(answer=[90, 0], question_id=question_id,
                                    submission_id=submission_id,
                                    survey_id=survey_id).execute()
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)
        condition = answer_table.c.answer_id == answer_id
        answer = answer_table.select().where(condition).execute().first()
        location = json.loads(get_geo_json(answer))['coordinates']
        self.assertEqual(location, [90, 0])

    def testGetAnswers(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_insert(answer=1, question_id=question_id,
                      submission_id=submission_id,
                      survey_id=survey_id).execute()
        self.assertEqual(get_answers(submission_id).rowcount, 1)


class TestAnswerChoice(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testAnswerChoiceInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(question_id)
        the_choice = choices.first()
        exec_stmt = answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id).execute()
        answer_id = exec_stmt.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testGetAnswerChoices(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(question_id)
        the_choice = choices.first()
        answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id).execute()
        self.assertEqual(get_answer_choices(submission_id).rowcount, 1)


# TODO: test auth_user.py

class TestLogicalConstraint(unittest.TestCase):
    def tearDown(self):
        column = logical_constraint_table.c.logical_constraint_name
        condition = column == 'test'
        logical_constraint_table.delete().where(condition).execute()

    def testLogicalConstraintExists(self):
        self.assertTrue(logical_constraint_exists(''))
        self.assertFalse(logical_constraint_exists('does not exist'))

    def testLogicalConstraintNameInsert(self):
        logical_constraint_name_insert('test').execute()
        column = logical_constraint_table.c.logical_constraint_name
        condition = column == 'test'
        exec_stmt = logical_constraint_table.select().where(condition)
        self.assertEqual(exec_stmt.execute().rowcount, 1)


class TestQuestion(unittest.TestCase):
    def tearDown(self):
        condition = question_table.c.title == 'test insert'
        question_table.delete().where(condition).execute()

    def testGetQuestion(self):
        survey_id = survey_table.select().execute().first().survey_id
        question_id = get_questions(survey_id).first().question_id
        question = get_question(question_id)
        self.assertEqual(question.question_id, question_id)

    def testGetQuestions(self):
        survey_id = survey_table.select().execute().first().survey_id
        questions = get_questions(survey_id)
        self.assertGreater(questions.rowcount, 0)

    def testGetFreeSequenceNumber(self):
        survey_id = survey_table.select().execute().first().survey_id
        self.assertEqual(get_free_sequence_number(survey_id), 10)

    def testQuestionInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        stmt = question_insert(hint=None, required=None, allow_multiple=None,
                               logical_constraint_name=None,
                               title='test insert',
                               type_constraint_name='text',
                               survey_id=survey_id)
        question_id = stmt.execute().inserted_primary_key[0]
        condition = question_table.c.title == 'test insert'
        self.assertEqual(question_table.select().where(
            condition).execute().first().question_id, question_id)


class TestQuestionBranch(unittest.TestCase):
    def testGetBranches(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        branches = get_branches(question_id)
        self.assertGreater(branches.rowcount, 0)


class TestQuestionChoice(unittest.TestCase):
    def testGetChoices(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        choices = get_choices(question_id)
        self.assertGreater(choices.rowcount, 0)


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testSubmissionSelect(self):
        survey_id = survey_table.select().execute().first().survey_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        submission = submission_select(submission_id)
        self.assertEqual(submission_id, submission.submission_id)

    def testGetSubmissions(self):
        survey_id = survey_table.select().execute().first().survey_id
        for _ in range(2):
            submission_exec = submission_insert(submitter='test_submitter',
                                                survey_id=survey_id).execute()
            submission_id = submission_exec.inserted_primary_key[0]
        submissions = get_submissions(survey_id)
        self.assertEqual(submissions.rowcount, 2)

    def testSubmissionInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        sub_exec = submission_table.select().where(
            submission_table.c.submission_id == submission_id).execute()
        submission = sub_exec.first()
        self.assertEqual(submission_id, submission.submission_id)


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        survey_table.delete().where(
            survey_table.c.title == 'test insert').execute()

    def testSurveySelect(self):
        survey = survey_table.select().execute().first()
        self.assertEqual(survey, survey_select(survey.survey_id))


    def testSurveyInsert(self):
        stmt = survey_insert(title='test insert')
        survey_id = stmt.execute().inserted_primary_key[0]
        condition = survey_table.c.title == 'test insert'
        get_stmt = survey_table.select().where(condition).execute().first()
        self.assertEqual(get_stmt.survey_id, survey_id)


class TestUtils(unittest.TestCase):
    def testDeleteRecord(self):
        exec_stmt = survey_insert(title='delete me').execute()
        survey_id = exec_stmt.inserted_primary_key[0]
        delete_record(survey_table, 'survey_id', survey_id).execute()
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 0)

    def testUpdateRecord(self):
        exec_stmt = survey_insert(title='update me').execute()
        survey_id = exec_stmt.inserted_primary_key[0]
        update_record(survey_table, 'survey_id', survey_id,
                      title='updated').execute()
        condition = survey_table.c.survey_id == survey_id
        new_record = survey_table.select().where(condition).execute().first()
        self.assertEqual(new_record.title, 'updated')
        self.assertNotEqual(new_record.survey_last_update_time,
                            new_record.created_on)
        delete_record(survey_table, 'survey_id', survey_id).execute()


if __name__ == '__main__':
    unittest.main()

