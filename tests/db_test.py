"""
Tests for the dokomo database

"""
import json
import unittest

from db.answer import answer_insert, answer_table, get_answers, get_geo_json
from db.answer_choice import answer_choice_insert, get_answer_choices
from db.question import get_questions, get_question, question_table
from db.question_branch import get_branches
from db.question_choice import get_choices
from db.submission import submission_insert, submission_table, submission_json
from db.survey import survey_table, survey_json

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
        answer_exec = answer_insert(answer='90 0', question_id=question_id,
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

class TestQuestion(unittest.TestCase):
    def testGetQuestion(self):
        survey_id = survey_table.select().execute().first().survey_id
        question_id = get_questions(survey_id).first().question_id
        question = get_question(question_id)
        self.assertEqual(question.question_id, question_id)

    def testGetQuestions(self):
        survey_id = survey_table.select().execute().first().survey_id
        questions = get_questions(survey_id)
        self.assertGreater(questions.rowcount, 0)


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

    def testSubmissionInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        sub_exec = submission_table.select().where(
            submission_table.c.submission_id == submission_id).execute()
        submission = sub_exec.first()
        self.assertEqual(submission_id, submission.submission_id)

    def testSubmissionJson(self):
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
        data = submission_json(submission_id)
        json_data = json.loads(data)
        self.assertIsNotNone(json_data['submission_id'])
        self.assertIsNotNone(json_data['answers'])


class TestSurvey(unittest.TestCase):
    def testSurveyJson(self):
        survey_id = survey_table.select().execute().first().survey_id
        data = survey_json(survey_id)
        json_data = json.loads(data)
        self.assertIsNotNone(json_data['survey_id'])
        self.assertIsNotNone(json_data['questions'])


if __name__ == '__main__':
    unittest.main()

