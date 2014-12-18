"""
Tests for the dokomo database

"""
from time import sleep
import unittest
import uuid
from sqlalchemy import cast, Text, Boolean
from datetime import datetime, timedelta

from passlib.hash import bcrypt_sha256

from db import update_record, delete_record
import db
from db.answer import answer_insert, answer_table, get_answers, get_geo_json
from db.answer_choice import answer_choice_insert, get_answer_choices
from db.auth_user import auth_user_table, get_auth_user, create_auth_user, \
    generate_api_token, set_api_token, verify_api_token
from db.question import get_questions, question_select, question_table, \
    get_free_sequence_number, question_insert
from db.question_branch import get_branches, question_branch_insert, \
    question_branch_table
from db.question_choice import get_choices, question_choice_select, \
    question_choice_insert, question_choice_table, \
    QuestionChoiceDoesNotExistError
from db.submission import submission_table, submission_insert, \
    submission_select, get_submissions
from db.survey import survey_table, survey_insert, survey_select


class TestAnswer(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testAnswerInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = answer_insert(answer=1, question_id=question_id,
                                    submission_id=submission_id,
                                    survey_id=survey_id,
                                    type_constraint_name=tcn,
                                    sequence_number=seq,
                                    allow_multiple=mul).execute()
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testInsertLocation(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'location')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = answer_insert(answer=[90, 0], question_id=question_id,
                                    submission_id=submission_id,
                                    survey_id=survey_id,
                                    type_constraint_name=tcn,
                                    sequence_number=seq,
                                    allow_multiple=mul).execute()
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)
        condition = answer_table.c.answer_id == answer_id
        answer = answer_table.select().where(condition).execute().first()
        location = get_geo_json(answer)['coordinates']
        self.assertEqual(location, [90, 0])

        submission_2_exec = submission_insert(submitter='test_submitter',
                                              survey_id=survey_id).execute()
        submission_2_id = submission_2_exec.inserted_primary_key[0]
        answer_2_exec = answer_insert(answer=None, question_id=question_id,
                                      submission_id=submission_2_id,
                                      survey_id=survey_id,
                                      type_constraint_name=tcn,
                                      sequence_number=seq,
                                      allow_multiple=mul).execute()
        answer_2_id = answer_2_exec.inserted_primary_key[0]
        condition_2 = answer_table.c.answer_id == answer_2_id
        answer_2 = answer_table.select().where(condition_2).execute().first()
        location_2 = get_geo_json(answer_2)
        self.assertEqual(location_2, {'coordinates': [], 'type': 'MultiPoint'})

    def testGetAnswers(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        answer_insert(answer=1, question_id=question_id,
                      submission_id=submission_id,
                      survey_id=survey_id, type_constraint_name=tcn,
                      sequence_number=seq, allow_multiple=mul).execute()
        self.assertEqual(get_answers(submission_id).rowcount, 1)


class TestAnswerChoice(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testAnswerChoiceInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(question_id)
        the_choice = choices.first()
        exec_stmt = answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul).execute()
        answer_id = exec_stmt.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testGetAnswerChoices(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = submission_insert(submitter='test_submitter',
                                            survey_id=survey_id).execute()
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(question_id)
        the_choice = choices.first()
        answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul).execute()
        self.assertEqual(get_answer_choices(submission_id).rowcount, 1)


class TestAuthUser(unittest.TestCase):
    def tearDown(self):
        auth_user_table.delete().where(
            auth_user_table.c.email != 'test_email').execute()

    def testGetAuthUser(self):
        result = auth_user_table.insert({'email': 'a'}).execute()
        user_id = result.inserted_primary_key[0]
        user = get_auth_user(user_id)
        self.assertEqual(user.email, 'a')

    def testCreateAuthUser(self):
        create_auth_user(email='a').execute()
        self.assertEqual(len(auth_user_table.select().where(
            auth_user_table.c.email == 'a').execute().fetchall()), 1)

    def testGenerateAPIToken(self):
        token_1 = generate_api_token()
        self.assertEqual(len(token_1), 32)

        token_2 = generate_api_token()
        self.assertNotEqual(token_1, token_2)

    def testSetAPIToken(self):
        result = auth_user_table.insert({'email': 'a'}).execute()
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        set_api_token(token=token, auth_user_id=user_id).execute()
        user = get_auth_user(user_id)
        self.assertTrue(bcrypt_sha256.verify(token, user.token))

    def testVerifyAPIToken(self):
        result = auth_user_table.insert({'email': 'a'}).execute()
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        set_api_token(token=token, auth_user_id=user_id).execute()
        self.assertTrue(verify_api_token(token=token, auth_user_id=user_id))
        self.assertFalse(
            verify_api_token(token=generate_api_token(), auth_user_id=user_id))

    def testNoDefaultToken(self):
        result = auth_user_table.insert({'email': 'a'}).execute()
        user_id = result.inserted_primary_key[0]
        self.assertFalse(
            verify_api_token(token=generate_api_token(), auth_user_id=user_id))

    def testTokenExpires(self):
        result = auth_user_table.insert({'email': 'a'}).execute()
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        exp = timedelta(seconds=0.5)
        set_api_token(token=token,
                      auth_user_id=user_id,
                      expiration=exp).execute()
        self.assertTrue(verify_api_token(token=token, auth_user_id=user_id))
        sleep(1.5)
        self.assertFalse(verify_api_token(token=token, auth_user_id=user_id))


class TestQuestion(unittest.TestCase):
    def tearDown(self):
        condition = question_table.c.title == 'test insert'
        question_table.delete().where(condition).execute()

    def testGetQuestion(self):
        survey_id = survey_table.select().execute().first().survey_id
        question_id = get_questions(survey_id).first().question_id
        question = question_select(question_id)
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
        sequence_number = get_free_sequence_number(survey_id)
        stmt = question_insert(hint=None, required=None, allow_multiple=None,
                               logic=None, sequence_number=sequence_number,
                               title='test insert',
                               type_constraint_name='text',
                               survey_id=survey_id)
        question_id = stmt.execute().inserted_primary_key[0]
        condition = question_table.c.title == 'test insert'
        self.assertEqual(question_table.select().where(
            condition).execute().first().question_id, question_id)


class TestQuestionBranch(unittest.TestCase):
    def tearDown(self):
        survey_id = survey_table.select().execute().first().survey_id
        to_question = get_questions(survey_id).fetchall()[-1]
        question_branch_table.delete().where(
            question_branch_table.c.to_question_id ==
            to_question.question_id).execute()

    def testGetBranches(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        branches = get_branches(question_id)
        self.assertGreater(branches.rowcount, 0)

    def testQuestionBranchInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        to_question = get_questions(survey_id).fetchall()[-1]
        q_where = question_table.select().where(
            cast(cast(question_table.c.logic['with_other'], Text), Boolean))
        from_question = q_where.execute().first()
        choice = get_choices(from_question.question_id).fetchall()[0]
        from_tcn = from_question.type_constraint_name
        branch_dict = {'question_choice_id': choice.question_choice_id,
                       'from_question_id': from_question.question_id,
                       'from_type_constraint': from_tcn,
                       'from_sequence_number': from_question.sequence_number,
                       'from_allow_multiple': from_question.allow_multiple,
                       'from_survey_id': survey_id,
                       'to_question_id': to_question.question_id,
                       'to_type_constraint': to_question.type_constraint_name,
                       'to_sequence_number': to_question.sequence_number,
                       'to_allow_multiple': to_question.allow_multiple,
                       'to_survey_id': survey_id}
        branch_exec = question_branch_insert(**branch_dict).execute()
        inserted_id = branch_exec.inserted_primary_key[0]
        the_branch = question_branch_table.select().where(
            question_branch_table.c.question_branch_id ==
            inserted_id).execute().first()
        self.assertEqual(the_branch.to_question_id, to_question.question_id)


class TestQuestionChoice(unittest.TestCase):
    def tearDown(self):
        condition = question_table.c.title == 'test choice'
        question_table.delete().where(condition).execute()

    def testGetChoices(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        choices = get_choices(question_id)
        self.assertGreater(choices.rowcount, 0)

    def testQuestionChoiceSelect(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = q_where.execute().first().question_id
        choice_id = get_choices(question_id).first().question_choice_id
        choice = question_choice_select(choice_id)
        self.assertIsNotNone(choice)

        self.assertRaises(QuestionChoiceDoesNotExistError,
                          question_choice_select, str(uuid.uuid4()))

    def testQuestionChoiceInsert(self):
        survey_id = survey_table.select().execute().first().survey_id
        seq_number = get_free_sequence_number(survey_id)
        stmt = question_insert(hint=None, required=None, allow_multiple=None,
                               logic=None, sequence_number=seq_number,
                               title='test choice',
                               type_constraint_name='multiple_choice',
                               survey_id=survey_id)
        question_id = stmt.execute().inserted_primary_key[0]
        c_stmt = question_choice_insert(question_id=question_id,
                                        choice='test choice',
                                        choice_number=1,
                                        type_constraint_name='multiple_choice',
                                        question_sequence_number=seq_number,
                                        allow_multiple=False,
                                        survey_id=survey_id)
        choice_id = c_stmt.execute().inserted_primary_key[0]
        cond = question_choice_table.c.question_id == question_id
        self.assertEqual(question_choice_table.select().where(
            cond).execute().first().question_choice_id, choice_id)


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
    def testSetTestingEngine(self):
        engine = db.engine
        db.set_testing_engine(None)
        self.assertIsNone(db.engine)
        db.set_testing_engine(engine)
        self.assertIsNotNone(db.engine)

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

        update_record(survey_table, 'survey_id', survey_id,
                      values_dict={'title': 'update2'}).execute()

        new_record = survey_table.select().where(condition).execute().first()
        self.assertEqual(new_record.title, 'update2')

        self.assertRaises(TypeError, update_record, survey_table, 'survey_id',
                          survey_id,
                          values_dict={'title': 'updated2'},
                          title='updated3')
        self.assertRaises(TypeError, update_record, survey_table, 'survey_id',
                          survey_id)

        delete_record(survey_table, 'survey_id', survey_id).execute()


if __name__ == '__main__':
    unittest.main()

