"""
Tests for the dokomo database

"""
import unittest
import uuid
from sqlalchemy import cast, Text, Boolean
from datetime import timedelta

from passlib.hash import bcrypt_sha256

from dokomoforms.db import update_record, delete_record
from dokomoforms import db
from dokomoforms.db.answer import answer_insert, answer_table, get_answers, \
    get_geo_json, \
    get_answers_for_question
from dokomoforms.db.answer_choice import answer_choice_insert, \
    get_answer_choices, \
    get_answer_choices_for_choice_id
from dokomoforms.db.auth_user import auth_user_table, get_auth_user, \
    create_auth_user, \
    generate_api_token, set_api_token, verify_api_token, \
    get_auth_user_by_email, \
    UserDoesNotExistError
from dokomoforms.db.question import get_questions_no_credentials, \
    question_select, \
    question_table, \
    get_free_sequence_number, question_insert, get_questions, \
    QuestionDoesNotExistError, get_required
from dokomoforms.db.question_branch import get_branches, \
    question_branch_insert, \
    question_branch_table
from dokomoforms.db.question_choice import get_choices, \
    question_choice_select, \
    question_choice_insert, question_choice_table, \
    QuestionChoiceDoesNotExistError
from dokomoforms.db.submission import submission_table, submission_insert, \
    submission_select, get_submissions_by_email, get_number_of_submissions, \
    SubmissionDoesNotExistError
from dokomoforms.db.survey import survey_table, survey_insert, survey_select, \
    get_surveys_by_email, display, SurveyDoesNotExistError, \
    get_survey_id_from_prefix, SurveyPrefixDoesNotIdentifyASurveyError, \
    SurveyPrefixTooShortError, get_email_address, get_free_title, \
    get_number_of_surveys


connection = db.engine.connect()


class TestAnswer(unittest.TestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def testAnswerInsert(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = connection.execute(answer_insert(
            answer=1, question_id=question_id,
            answer_metadata={},
            submission_id=submission_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=False,
            sequence_number=seq,
            allow_multiple=mul))
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testAnswerInsertNoMetadata(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = connection.execute(answer_insert(
            answer=1, question_id=question_id,
            answer_metadata=None,
            submission_id=submission_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=False,
            sequence_number=seq,
            allow_multiple=mul))
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testAnswerInsertOther(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = connection.execute(answer_insert(
            answer='one', question_id=question_id,
            answer_metadata={},
            submission_id=submission_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=True,
            sequence_number=seq,
            allow_multiple=mul))
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testInsertLocation(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'location')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = connection.execute(answer_insert(
            answer={'lon': 90, 'lat': 0},
            answer_metadata={},
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=False,
            sequence_number=seq,
            allow_multiple=mul))
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)
        condition = answer_table.c.answer_id == answer_id
        answer = connection.execute(
            answer_table.select().where(condition)).first()
        location = get_geo_json(connection, answer)['coordinates']
        self.assertEqual(location, [90, 0])

        submission_2_exec = connection.execute(
            submission_insert(submitter='test_submitter', survey_id=survey_id))
        submission_2_id = submission_2_exec.inserted_primary_key[0]
        answer_2_exec = connection.execute(answer_insert(
            answer=None, question_id=question_id,
            answer_metadata={},
            submission_id=submission_2_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=False,
            sequence_number=seq,
            allow_multiple=mul))
        answer_2_id = answer_2_exec.inserted_primary_key[0]
        condition_2 = answer_table.c.answer_id == answer_2_id
        answer_2 = connection.execute(
            answer_table.select().where(condition_2)).first()
        location_2 = get_geo_json(connection, answer_2)
        self.assertEqual(location_2,
                         {'coordinates': [], 'type': 'MultiPoint'})

    def testInsertFacility(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'facility')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        answer_exec = connection.execute(answer_insert(
            answer={'id': 'revisit ID', 'lon': 90, 'lat': 0},
            answer_metadata={'facility_name': 'cool facility',
                             'facility_sector': 'health'},
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id,
            type_constraint_name=tcn,
            is_other=False,
            sequence_number=seq,
            allow_multiple=mul))
        answer_id = answer_exec.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)
        condition = answer_table.c.answer_id == answer_id
        answer = connection.execute(
            answer_table.select().where(condition)).first()
        location = get_geo_json(connection, answer)['coordinates']
        self.assertEqual(location, [90, 0])
        facility_id = answer.answer_text
        self.assertEqual(facility_id, 'revisit ID')

    def testGetAnswers(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        connection.execute(answer_insert(answer=1, question_id=question_id,
                                         answer_metadata={},
                                         submission_id=submission_id,
                                         survey_id=survey_id,
                                         type_constraint_name=tcn,
                                         is_other=False,
                                         sequence_number=seq,
                                         allow_multiple=mul))
        self.assertEqual(get_answers(connection, submission_id).rowcount, 1)

    def testGetAnswersForQuestion(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter',
                              survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        connection.execute(answer_insert(answer=1, question_id=question_id,
                                         answer_metadata={},
                                         submission_id=submission_id,
                                         survey_id=survey_id,
                                         type_constraint_name=tcn,
                                         is_other=False,
                                         sequence_number=seq,
                                         allow_multiple=mul))
        self.assertEqual(
            get_answers_for_question(connection, question_id).rowcount, 1)


class TestAnswerChoice(unittest.TestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def testAnswerChoiceInsert(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(connection, question_id)
        the_choice = choices.first()
        exec_stmt = connection.execute(answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            answer_choice_metadata={},
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul))
        answer_id = exec_stmt.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testAnswerChoiceInsertNoMetadata(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(connection, question_id)
        the_choice = choices.first()
        exec_stmt = connection.execute(answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            answer_choice_metadata=None,
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul))
        answer_id = exec_stmt.inserted_primary_key[0]
        self.assertIsNotNone(answer_id)

    def testGetAnswerChoices(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(connection, question_id)
        the_choice = choices.first()
        connection.execute(answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            answer_choice_metadata={},
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul))
        self.assertEqual(
            get_answer_choices(connection, submission_id).rowcount, 1)

    def testGetAnswerChoicesForChoiceId(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        choices = get_choices(connection, question_id)
        the_choice = choices.first()
        connection.execute(answer_choice_insert(
            question_choice_id=the_choice.question_choice_id,
            answer_choice_metadata={},
            question_id=question_id,
            submission_id=submission_id,
            survey_id=survey_id, type_constraint_name=tcn, sequence_number=seq,
            allow_multiple=mul))
        gacfci = get_answer_choices_for_choice_id
        actual_choices = gacfci(connection, the_choice.question_choice_id)
        self.assertEqual(actual_choices.rowcount, 1)


class TestAuthUser(unittest.TestCase):
    def tearDown(self):
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email.in_(('a',))))

    def testGetAuthUser(self):
        result = connection.execute(auth_user_table.insert({'email': 'a'}))
        user_id = result.inserted_primary_key[0]
        user = get_auth_user(connection, user_id)
        self.assertEqual(user.email, 'a')

    def testNoGetAuthUser(self):
        fake_id = str(uuid.uuid4())
        self.assertRaises(UserDoesNotExistError, get_auth_user,
                          connection,
                          fake_id)

    def testGetAuthUserByEmail(self):
        connection.execute(auth_user_table.insert({'email': 'a'}))
        user = get_auth_user_by_email(connection, 'a')
        self.assertEqual(user.email, 'a')

    def testCreateAuthUser(self):
        connection.execute(create_auth_user(email='a'))
        self.assertEqual(len(connection.execute(
            auth_user_table.select().where(
                auth_user_table.c.email == 'a')).fetchall()), 1)

    def testGenerateAPIToken(self):
        token_1 = generate_api_token()
        self.assertEqual(len(token_1), 32)
        token_2 = generate_api_token()
        self.assertNotEqual(token_1, token_2)

    def testSetAPIToken(self):
        result = connection.execute(auth_user_table.insert({'email': 'a'}))
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        connection.execute(set_api_token(token=token, auth_user_id=user_id))
        user = get_auth_user(connection, user_id)
        self.assertTrue(bcrypt_sha256.verify(token, user.token))

    def testVerifyAPIToken(self):
        result = connection.execute(auth_user_table.insert({'email': 'a'}))
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        connection.execute(set_api_token(token=token, auth_user_id=user_id))
        self.assertTrue(
            verify_api_token(connection, token=token, email='a'))
        self.assertFalse(
            verify_api_token(connection, token=generate_api_token(),
                             email='a'))

    def testVerifyAPITokenWhenEmailDoesNotExist(self):
        self.assertFalse(
            verify_api_token(connection, token=generate_api_token(),
                             email='nope'))

    def testNoDefaultToken(self):
        connection.execute(auth_user_table.insert({'email': 'a'}))
        self.assertFalse(
            verify_api_token(connection, token=generate_api_token(),
                             email='a'))

    def testTokenExpires(self):
        result = connection.execute(auth_user_table.insert({'email': 'a'}))
        user_id = result.inserted_primary_key[0]
        token = generate_api_token()
        exp = timedelta(hours=1)
        connection.execute(
            set_api_token(token=token, auth_user_id=user_id, expiration=exp))
        self.assertTrue(
            verify_api_token(connection, token=token, email='a'))
        token2 = generate_api_token()
        exp2 = timedelta(hours=-1)
        connection.execute(set_api_token(
            token=token2,
            auth_user_id=user_id,
            expiration=exp2))
        self.assertFalse(
            verify_api_token(connection, token=token2, email='a'))


class TestQuestion(unittest.TestCase):
    def tearDown(self):
        condition = question_table.c.question_title == 'test insert'
        connection.execute(question_table.delete().where(condition))

    def testQuestionSelect(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        question_id = get_questions_no_credentials(
            connection, survey_id).first().question_id
        question = question_select(connection, question_id)
        self.assertEqual(question.question_id, question_id)

    def testQuestionSelectDoesNotExist(self):
        self.assertRaises(QuestionDoesNotExistError, question_select,
                          connection,
                          str(uuid.uuid4()))

    def testGetQuestions(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        questions = get_questions(connection, survey_id,
                                  email='test_email')
        self.assertGreater(questions.rowcount, 0)

        auth_user_id = get_auth_user_by_email(connection,
                                              'test_email').auth_user_id
        questions = get_questions(connection, survey_id,
                                  auth_user_id=auth_user_id)
        self.assertGreater(questions.rowcount, 0)

        self.assertRaises(TypeError, get_questions, connection, survey_id)
        self.assertRaises(TypeError, get_questions, connection, survey_id,
                          auth_user_id='',
                          email='')

    def testGetQuestionsNoCredentials(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        questions = get_questions_no_credentials(connection, survey_id)
        self.assertGreater(questions.rowcount, 0)

    def testGetFreeSequenceNumber(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        self.assertEqual(
            get_free_sequence_number(connection, survey_id),
            11)

    def testQuestionInsert(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        sequence_number = get_free_sequence_number(connection,
                                                   survey_id)
        stmt = question_insert(hint=None, allow_multiple=None,
                               logic={'required': False,
                                      'with_other': False},
                               sequence_number=sequence_number,
                               question_title='test insert',
                               type_constraint_name='text',
                               question_to_sequence_number=sequence_number + 1,
                               survey_id=survey_id)
        question_id = connection.execute(stmt).inserted_primary_key[0]
        condition = question_table.c.question_title == 'test insert'
        self.assertEqual(connection.execute(question_table.select().where(
            condition)).first().question_id, question_id)

    def testNoLogic(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        sequence_number = get_free_sequence_number(connection,
                                                   survey_id)
        with self.assertRaises(TypeError) as exc:
            question_insert(hint=None,
                            allow_multiple=None,
                            logic=None,
                            sequence_number=sequence_number,
                            question_to_sequence_number=1,
                            question_title='test insert',
                            type_constraint_name='text',
                            survey_id=survey_id)
        self.assertEqual(str(exc.exception), 'logic must not be None')

    def testGetRequired(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'what is life')).first().survey_id
        reqs = get_required(connection, survey_id)
        self.assertEqual(reqs.rowcount, 2)


class TestQuestionBranch(unittest.TestCase):
    def tearDown(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        to_question = get_questions_no_credentials(
            connection, survey_id).fetchall()[-1]
        connection.execute(question_branch_table.delete().where(
            question_branch_table.c.to_question_id ==
            to_question.question_id))

    def testGetBranches(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = connection.execute(q_where).first().question_id
        branches = get_branches(connection, question_id)
        self.assertGreater(branches.rowcount, 0)

    def testQuestionBranchInsert(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        to_question = get_questions_no_credentials(
            connection, survey_id).fetchall()[-1]
        q_where = question_table.select().where(
            cast(cast(question_table.c.logic['with_other'], Text),
                 Boolean))
        from_question = connection.execute(q_where).fetchall()[1]
        choice = get_choices(
            connection, from_question.question_id).fetchall()[0]
        from_tcn = from_question.type_constraint_name
        branch_dict = {'question_choice_id': choice.question_choice_id,
                       'from_question_id': from_question.question_id,
                       'from_type_constraint': from_tcn,
                       'from_sequence_number':
                           from_question.sequence_number,
                       'from_allow_multiple':
                           from_question.allow_multiple,
                       'from_survey_id': survey_id,
                       'to_question_id': to_question.question_id,
                       'to_type_constraint':
                           to_question.type_constraint_name,
                       'to_sequence_number':
                           to_question.sequence_number,
                       'to_allow_multiple': to_question.allow_multiple,
                       'to_survey_id': survey_id}
        branch_exec = connection.execute(question_branch_insert(**branch_dict))
        inserted_id = branch_exec.inserted_primary_key[0]
        the_branch = connection.execute(question_branch_table.select().where(
            question_branch_table.c.question_branch_id ==
            inserted_id)).first()
        self.assertEqual(the_branch.to_question_id,
                         to_question.question_id)


class TestQuestionChoice(unittest.TestCase):
    def tearDown(self):
        condition = question_table.c.question_title == 'test choice'
        connection.execute(question_table.delete().where(condition))

    def testGetChoices(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = connection.execute(q_where).first().question_id
        choices = get_choices(connection, question_id)
        self.assertGreater(choices.rowcount, 0)

    def testQuestionChoiceSelect(self):
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'multiple_choice')
        question_id = connection.execute(q_where).first().question_id
        choice_id = get_choices(connection,
                                question_id).first().question_choice_id
        choice = question_choice_select(connection, choice_id)
        self.assertIsNotNone(choice)

        self.assertRaises(QuestionChoiceDoesNotExistError,
                          question_choice_select, connection,
                          str(uuid.uuid4()))

    def testQuestionChoiceInsert(self):
        survey_id = connection.execute(
            survey_table.select().where(
                survey_table.c.survey_title == 'test_title'
            )).first().survey_id
        seq_number = get_free_sequence_number(connection, survey_id)
        stmt = question_insert(hint=None, allow_multiple=None,
                               logic={'required': False,
                                      'with_other': False},
                               sequence_number=seq_number,
                               question_title='test choice',
                               type_constraint_name='multiple_choice',
                               question_to_sequence_number=-1,
                               survey_id=survey_id)
        question_id = connection.execute(stmt).inserted_primary_key[0]
        c_stmt = question_choice_insert(question_id=question_id,
                                        choice='test choice',
                                        choice_number=1,
                                        type_constraint_name='multiple_choice',
                                        question_sequence_number=seq_number,
                                        allow_multiple=False,
                                        survey_id=survey_id)
        choice_id = connection.execute(c_stmt).inserted_primary_key[0]
        cond = question_choice_table.c.question_id == question_id
        self.assertEqual(connection.execute(
            question_choice_table.select().where(cond)
        ).first().question_choice_id, choice_id)


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        connection.execute(submission_table.delete())

    def testSubmissionSelect(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        submission = submission_select(connection, submission_id,
                                       email='test_email')
        self.assertEqual(submission_id, submission.submission_id)
        user_id = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().auth_user_id
        submission2 = submission_select(connection, submission_id,
                                        auth_user_id=user_id)
        self.assertEqual(submission_id,
                         submission2.submission_id)
        self.assertRaises(TypeError, submission_select, connection,
                          submission_id,
                          auth_user_id='', email='')
        self.assertRaises(TypeError, submission_select, connection,
                          submission_id)

    def testSubmissionSelectDoesNotExist(self):
        self.assertRaises(SubmissionDoesNotExistError,
                          submission_select,
                          connection,
                          str(uuid.uuid4()), email='test_email')

    def testGetSubmissionsByEmail(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        for i in range(2):
            connection.execute(submission_insert(
                submitter='test_submitter{}'.format(i), survey_id=survey_id))
        submissions = get_submissions_by_email(connection, survey_id,
                                               email='test_email')
        self.assertEqual(submissions.rowcount, 2)
        submissions = get_submissions_by_email(connection, survey_id,
                                               email='test_email',
                                               submitters=[
                                                   'test_submitter1'])
        self.assertEqual(submissions.rowcount, 1)

    def testGetSubmissionsWithFilter(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = connection.execute(q_where).first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        for i in range(2):
            submission_exec = connection.execute(submission_insert(
                submitter='test_submitter',
                survey_id=survey_id))
            submission_id = submission_exec.inserted_primary_key[0]
            connection.execute(answer_insert(
                answer=i, question_id=question_id, submission_id=submission_id,
                answer_metadata={},
                survey_id=survey_id, type_constraint_name=tcn, is_other=False,
                sequence_number=seq, allow_multiple=mul))
        self.assertEqual(
            len(get_submissions_by_email(connection, survey_id,
                                         email='test_email').fetchall()),
            2)
        f_result = get_submissions_by_email(connection, survey_id,
                                            email='test_email',
                                            filters=[
                                                {
                                                    'question_id':
                                                        question_id,
                                                    'answer_integer':
                                                        1}]).fetchall()
        self.assertEqual(len(f_result), 1)

    def testSubmissionInsert(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        sub_exec = connection.execute(submission_table.select().where(
            submission_table.c.submission_id ==
            submission_id))
        submission = sub_exec.first()
        self.assertEqual(submission_id, submission.submission_id)

    def testSubmissionInsertWithSubmissionTime(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        time = '2015-02-17 04:44:00'
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id,
            submission_time=time))
        submission_id = submission_exec.inserted_primary_key[0]
        sub_exec = connection.execute(submission_table.select().where(
            submission_table.c.submission_id ==
            submission_id))
        submission = sub_exec.first()
        self.assertEqual(submission_id, submission.submission_id)

    def testSubmissionInsertWithFieldUpdateTime(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        time = '2015-02-17 04:44:00'
        submission_exec = connection.execute(submission_insert(
            submitter='test_submitter', survey_id=survey_id,
            field_update_time=time))
        submission_id = submission_exec.inserted_primary_key[0]
        sub_exec = connection.execute(
            submission_table.select().where(
                submission_table.c.submission_id == submission_id))
        submission = sub_exec.first()
        self.assertEqual(submission_id, submission.submission_id)

    def testGetNumberOfSubmissions(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        submission_exec = connection.execute(
            submission_insert(submitter='test_submitter', survey_id=survey_id))
        submission_id = submission_exec.inserted_primary_key[0]
        connection.execute(submission_table.select().where(
            submission_table.c.submission_id ==
            submission_id))
        self.assertEqual(get_number_of_submissions(connection, survey_id), 1)


class TestSurvey(unittest.TestCase):
    def tearDown(self):
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title.like('test insert%')))
        connection.execute(auth_user_table.delete().where(
            auth_user_table.c.email == 'TestSurveyEmail'
        ))

    def testGetSurveysForUserByEmail(self):
        user = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first()
        condition = survey_table.c.auth_user_id == user.auth_user_id
        surveys = connection.execute(survey_table.select().where(
            condition)).fetchall()
        surveys_by_email = get_surveys_by_email(connection, user.email)
        self.assertEqual(len(surveys), len(surveys_by_email))
        self.assertEqual(surveys[0].survey_id,
                         surveys_by_email[0].survey_id)

    def testGetNumberOfSurveys(self):
        number_of_surveys = get_number_of_surveys(connection, 'test_email')
        self.assertEqual(number_of_surveys, 1)

        connection.execute(create_auth_user(email='TestSurveyEmail'))
        zero_surveys = get_number_of_surveys(connection, 'TestSurveyEmail')
        self.assertEqual(zero_surveys, 0)

    def testGetSurveyIdFromPrefix(self):
        survey_id = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first().survey_id
        self.assertEqual(
            get_survey_id_from_prefix(connection, survey_id[:10]),
            survey_id)
        self.assertRaises(SurveyPrefixDoesNotIdentifyASurveyError,
                          get_survey_id_from_prefix, connection,
                          str(uuid.uuid4()))

    def testPrefixTooShort(self):
        self.assertRaises(SurveyPrefixTooShortError,
                          get_survey_id_from_prefix, connection,
                          'a')

    def testDisplay(self):
        survey = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first()
        self.assertEqual(survey.survey_title,
                         display(connection,
                                 survey.survey_id).survey_title)
        self.assertRaises(SurveyDoesNotExistError, display, connection,
                          str(uuid.uuid4()))

    def testSurveySelect(self):
        user = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first()
        survey = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first()
        self.assertEqual(survey.survey_title,
                         survey_select(connection, survey.survey_id,
                                       auth_user_id=user.auth_user_id)
                         .survey_title)
        self.assertEqual(survey.survey_title,
                         survey_select(connection, survey.survey_id,
                                       email=user.email).survey_title)
        self.assertRaises(TypeError, survey_select, connection,
                          survey.survey_id,
                          auth_user_id=user.auth_user_id,
                          email=user.email)
        self.assertRaises(TypeError, survey_select, connection,
                          survey.survey_id)

    def testSurveySelectDoesNotExist(self):
        self.assertRaises(SurveyDoesNotExistError, survey_select,
                          connection,
                          str(uuid.uuid4()), email='test_email')

    def testSurveyInsert(self):
        auth_user_id = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().auth_user_id
        stmt = survey_insert(survey_title='test insert',
                             survey_metadata=None,
                             auth_user_id=auth_user_id)
        survey_id = connection.execute(stmt).inserted_primary_key[0]
        condition = survey_table.c.survey_title == 'test insert'
        get_stmt = connection.execute(
            survey_table.select().where(condition)).first()
        self.assertEqual(get_stmt.survey_id, survey_id)

    def testGetFreeTitle(self):
        auth_user_id = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().auth_user_id

        self.assertEqual(
            get_free_title(connection, 'test insert', auth_user_id),
            'test insert')

        stmt = survey_insert(survey_title='test insert',
                             survey_metadata={},
                             auth_user_id=auth_user_id)
        connection.execute(stmt)
        self.assertEqual(
            get_free_title(connection, 'test insert', auth_user_id),
            'test insert(1)')
        stmt2 = survey_insert(survey_title='test insert(1)',
                              survey_metadata={},
                              auth_user_id=auth_user_id)
        connection.execute(stmt2)
        self.assertEqual(
            get_free_title(connection, 'test insert', auth_user_id),
            'test insert(2)')

    def testGetEmailAddress(self):
        survey = connection.execute(survey_table.select().where(
            survey_table.c.survey_title == 'test_title')).first()
        self.assertEqual(
            get_email_address(connection, survey.survey_id),
            'test_email')


class TestUtils(unittest.TestCase):
    def tearDown(self):
        connection.execute(survey_table.delete().where(
            survey_table.c.survey_title == 'update2'))

    def testGeometryColumn(self):
        geom = db.Geometry()
        self.assertEqual(geom.get_col_spec(), 'GEOMETRY')

    def testSetTestingEngine(self):
        engine = db.engine
        db.set_testing_engine(None)
        self.assertIsNone(db.engine)
        db.set_testing_engine(engine)
        self.assertIsNotNone(db.engine)

    def testGetColumn(self):
        self.assertIs(db.get_column(answer_table, 'answer_integer'),
                      answer_table.c.answer_integer)
        self.assertRaises(db.NoSuchColumnError, db.get_column,
                          answer_table,
                          'garbage')

    def testDeleteRecord(self):
        auth_user_id = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().auth_user_id
        exec_stmt = connection.execute(survey_insert(
            survey_title='delete me',
            survey_metadata={},
            auth_user_id=auth_user_id))
        survey_id = exec_stmt.inserted_primary_key[0]
        connection.execute(delete_record(survey_table, 'survey_id', survey_id))
        condition = survey_table.c.survey_id == survey_id
        self.assertEqual(
            connection.execute(
                survey_table.select().where(condition)).rowcount,
            0)

    def testUpdateRecord(self):
        auth_user_id = connection.execute(auth_user_table.select().where(
            auth_user_table.c.email == 'test_email')).first().auth_user_id
        exec_stmt = connection.execute(survey_insert(
            survey_title='update me',
            survey_metadata={},
            auth_user_id=auth_user_id))
        survey_id = exec_stmt.inserted_primary_key[0]
        connection.execute(update_record(survey_table, 'survey_id', survey_id,
                                         survey_title='updated'))
        condition = survey_table.c.survey_id == survey_id
        new_record = connection.execute(
            survey_table.select().where(condition)).first()
        self.assertEqual(new_record.survey_title, 'updated')
        self.assertNotEqual(new_record.survey_last_update_time,
                            new_record.created_on)

        connection.execute(update_record(
            survey_table, 'survey_id', survey_id,
            values_dict={'survey_title': 'update2'}))

        new_record = connection.execute(survey_table.select().where(
            condition)).first()
        self.assertEqual(new_record.survey_title, 'update2')

        self.assertRaises(TypeError, update_record, survey_table,
                          'survey_id',
                          survey_id,
                          values_dict={'survey_title': 'updated2'},
                          survey_title='updated3')
        self.assertRaises(TypeError, update_record, survey_table,
                          'survey_id',
                          survey_id)

        connection.execute(delete_record(survey_table, 'survey_id', survey_id))

        if __name__ == '__main__':
            unittest.main()
