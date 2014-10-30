"""
Tests for the dokomo JSON api

"""
import unittest
import uuid
from sqlalchemy import and_

from sqlalchemy.exc import DataError

import api.survey
import api.submission
from db.answer import answer_insert, CannotAnswerMultipleTimes
from db.question import question_table, get_questions, \
    QuestionDoesNotExistError
from db.question_branch import get_branches, MultipleBranchError
from db.question_choice import question_choice_table, get_choices, \
    RepeatedChoiceError, QuestionChoiceDoesNotExistError
from db.submission import submission_table, submission_insert, \
    SubmissionDoesNotExistError, submission_select
from db.survey import survey_table, survey_select, SurveyDoesNotExistError
from db.type_constraint import TypeConstraintDoesNotExistError


class TestSubmission(unittest.TestCase):
    def tearDown(self):
        submission_table.delete().execute()

    def testSubmit(self):
        survey_id = survey_table.select().execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        second_cond = and_(question_table.c.survey_id == survey_id,
                           question_table.c.type_constraint_name ==
                           'multiple_choice')
        second_q_id = question_table.select().where(
            second_cond).execute().first().question_id
        choice_cond = question_choice_table.c.question_id == second_q_id
        choice_id = question_choice_table.select().where(
            choice_cond).execute().first().question_choice_id
        third_cond = second_cond = and_(
            question_table.c.survey_id == survey_id,
            question_table.c.type_constraint_name ==
            'text')
        third_q_id = question_table.select().where(
            third_cond).execute().first().question_id
        input_data = {'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 1},
                           {'question_id': second_q_id,
                            'question_choice_id': choice_id},
                           {'question_id': third_q_id,
                            'answer': 'answer one'},
                           {'question_id': third_q_id,
                            'answer': 'answer two'}]}
        response = api.submission.submit(input_data)
        submission_id = response['submission_id']
        condition = submission_table.c.submission_id == submission_id
        self.assertEqual(
            submission_table.select().where(condition).execute().rowcount, 1)
        data = api.submission.get(submission_id)
        self.assertEqual(response, data)
        self.assertEqual(data['answers'][1]['question_choice_id'], choice_id)
        self.assertEqual(data['answers'][2]['question_id'], third_q_id)
        self.assertEqual(data['answers'][3]['question_id'], third_q_id)

    def testIncorrectType(self):
        survey_id = survey_table.select().execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        input_data = {'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 'one'}]}
        self.assertRaises(DataError, api.submission.submit, input_data)
        self.assertEqual(submission_table.select().execute().rowcount, 0)

    def testQuestionDoesNotExist(self):
        survey_id = survey_table.select().execute().first().survey_id
        input_data = {'survey_id': survey_id,
                      'answers': [{'question_id': str(uuid.uuid4()),
                                   'answer': 1}]}
        self.assertRaises(QuestionDoesNotExistError, api.submission.submit,
                          input_data)

    def testSurveyDoesNotExist(self):
        survey_id = str(uuid.uuid4())
        input_data = {'survey_id': survey_id, 'answers': []}
        self.assertRaises(SurveyDoesNotExistError, api.submission.submit,
                          input_data)

    def testDateAndTime(self):
        survey_id = survey_table.select().execute().first().survey_id
        date_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'date')
        date_question_id = question_table.select().where(
            date_cond).execute().first().question_id
        time_cond = and_(question_table.c.survey_id == survey_id,
                         question_table.c.type_constraint_name == 'time')
        time_question_id = question_table.select().where(
            time_cond).execute().first().question_id
        input_data = {'survey_id': survey_id,
                      'answers':
                          [{'question_id': date_question_id,
                            'answer': '2014-10-27'},
                           {'question_id': time_question_id,
                            'answer': '11:26-04:00'}]}  # UTC-04:00
        response = api.submission.submit(input_data)
        self.assertEqual(response['answers'][0]['answer'], '2014-10-27')
        self.assertEqual(response['answers'][1]['answer'], '11:26:00-04:00')

    def testOnlyAllowMultiple(self):
        survey_id = survey_table.select().execute().first().survey_id
        and_cond = and_(question_table.c.survey_id == survey_id,
                        question_table.c.type_constraint_name == 'integer')
        question_id = question_table.select().where(
            and_cond).execute().first().question_id
        input_data = {'survey_id': survey_id,
                      'answers':
                          [{'question_id': question_id,
                            'answer': 1},
                           {'question_id': question_id,
                            'answer': 2}]}
        self.assertRaises(CannotAnswerMultipleTimes, api.submission.submit,
                          input_data)


    def testGet(self):
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
        answer_insert(answer=[90, 0], question_id=question_id,
                      submission_id=submission_id,
                      survey_id=survey_id, type_constraint_name=tcn,
                      sequence_number=seq, allow_multiple=mul).execute()
        data = api.submission.get(submission_id)
        self.assertIsNotNone(data['submission_id'])
        self.assertIsNotNone(data['answers'])

    def testGetForSurvey(self):
        survey_id = survey_table.select().execute().first().survey_id
        q_where = question_table.select().where(
            question_table.c.type_constraint_name == 'integer')
        question = q_where.execute().first()
        question_id = question.question_id
        tcn = question.type_constraint_name
        seq = question.sequence_number
        mul = question.allow_multiple
        for i in range(2):
            submission_exec = submission_insert(submitter='test_submitter',
                                                survey_id=survey_id).execute()
            submission_id = submission_exec.inserted_primary_key[0]
            answer_insert(answer=i, question_id=question_id,
                          submission_id=submission_id,
                          survey_id=survey_id, type_constraint_name=tcn,
                          sequence_number=seq, allow_multiple=mul).execute()
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
        questions = [{'title': 'api_test mc question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': {},
                      'choices': ['choice 1', 'choice 2'],
                      'branches': [{'choice_number': 0,
                                    'to_question_number': 1}]
                     },
                     {'title': 'api_test question',
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
        questions = list(get_questions(survey_id))
        self.assertEqual(questions[1].logic, {'min': 3})
        self.assertEqual(get_choices(questions[0].question_id).first().choice,
                         'choice 1')

    def testSurveyAlreadyExists(self):
        survey_id = survey_table.select().execute().first().survey_id
        title = survey_select(survey_id).title
        input_data = {'title': title}
        result = api.survey.create(input_data)
        self.assertEqual(result['title'], 'test_title(1)')
        result2 = api.survey.create(input_data)
        self.assertEqual(result2['title'], 'test_title(2)')
        result3 = api.survey.create({'title': 'test_title(1)'})
        self.assertEqual(result3['title'], 'test_title(1)(1)')

        api.survey.create({'title': 'not in conflict(1)'})
        result4 = api.survey.create({'title': 'not in conflict'})
        self.assertEqual(result4['title'], 'not in conflict')

    def testTwoChoicesWithSameName(self):
        input_data = {'title': 'choice error',
                      'questions': [{'title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'hint': None,
                                     'required': None,
                                     'allow_multiple': None,
                                     'logic': {},
                                     'choices': ['a', 'a']}]}
        self.assertRaises(RepeatedChoiceError, api.survey.create, input_data)

    def testTwoBranchesFromOneChoice(self):
        input_data = {'title': 'choice error',
                      'questions': [{'title': 'choice error',
                                     'type_constraint_name': 'multiple_choice',
                                     'sequence_number': None,
                                     'hint': None,
                                     'required': None,
                                     'allow_multiple': None,
                                     'logic': None,
                                     'choices': ['a', 'b'],
                                     'branches': [{'choice_number': 0,
                                                   'to_question_number': 1},
                                                  {'choice_number': 0,
                                                   'to_question_number': 2}]},
                                    {'title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'hint': None,
                                     'required': None,
                                     'allow_multiple': None,
                                     'logic': None},
                                    {'title': 'choice error',
                                     'type_constraint_name': 'text',
                                     'sequence_number': None,
                                     'hint': None,
                                     'required': None,
                                     'allow_multiple': None,
                                     'logic': None}]}
        self.assertRaises(MultipleBranchError, api.survey.create, input_data)

    def testTypeConstraintDoesNotExist(self):
        input_data = {'title': 'type constraint error',
                      'questions': [{'title': 'type constraint error',
                                     'type_constraint_name': 'not real',
                                     'sequence_number': None,
                                     'hint': None,
                                     'required': None,
                                     'allow_multiple': None,
                                     'logic': {}}]}
        self.assertRaises(TypeConstraintDoesNotExistError, api.survey.create,
                          input_data)
        condition = survey_table.c.title == 'type constraint error'
        self.assertEqual(
            survey_table.select().where(condition).execute().rowcount, 0)

    def testUpdate(self):
        questions = [{'title': 'api_test question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None},
                     {'title': 'api_test 2nd question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None,
                      'choices': ['1', '2', '3'],
                      'branches': [
                          {'choice_number': 0, 'to_question_number': 2}]},
                     {'title': 'api_test 3rd question',
                      'type_constraint_name': 'text',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None}]
        data = {'title': 'api_test survey',
                'questions': questions}
        survey_id = api.survey.create(data)['survey_id']
        inserted_questions = get_questions(survey_id).fetchall()

        update_json = {'survey_id': survey_id,
                       'title': 'updated survey title'}
        questions = [{'question_id': inserted_questions[1].question_id,
                      'title': 'api_test 2nd question',
                      'type_constraint_name': 'multiple_choice',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': {'max': 'one'},
                      'choices': [{'old_choice': '2', 'new_choice': 'b'},
                                  'a',
                                  '1'],
                      'branches': [
                          {'choice_number': 1, 'to_question_number': 2}]},
                     {'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': None,
                      'type_constraint_name': 'text'},
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
        upd_questions = get_questions(survey_id).fetchall()
        branch = get_branches(inserted_questions[1].question_id).first()
        self.assertEqual(branch.to_question_id, upd_questions[2].question_id)
        self.assertEqual(upd_questions[0].title, 'api_test 2nd question')
        self.assertEqual(upd_questions[0].logic, {'max': 'one'})
        self.assertEqual(upd_survey.title, 'updated survey title')
        self.assertEqual(upd_questions[1].title, 'updated question title')
        choices = get_choices(inserted_questions[1].question_id).fetchall()
        self.assertEqual(choices[0].choice, 'b')
        self.assertEqual(choices[1].choice, 'a')
        self.assertEqual(choices[2].choice, '1')
        self.assertEqual(len(choices), 3)

    def testUpdateBadChoices(self):
        questions = [{'title': 'bad update question',
                      'type_constraint_name': 'multiple_choice',
                      'sequence_number': None,
                      'hint': None,
                      'required': None,
                      'allow_multiple': None,
                      'logic': None,
                      'choices': ['one', 'two']}]
        data = {'title': 'bad update survey',
                'questions': questions}
        survey_id = api.survey.create(data)['survey_id']
        inserted_questions = get_questions(survey_id).fetchall()

        update_json = {'survey_id': survey_id,
                       'title': 'updated survey title'}
        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': None,
                      'type_constraint_name': 'multiple_choice',
                      'choices': ['two', 'one', 'one']}]
        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': None,
                      'type_constraint_name': 'multiple_choice',
                      'choices': [
                          {'old_choice': 'three', 'new_choice': 'four'}]}]

        update_json['questions'] = questions
        self.assertRaises(QuestionChoiceDoesNotExistError, api.survey.update,
                          update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': None,
                      'type_constraint_name': 'multiple_choice',
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'}, 'two']}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)

        questions = [{'question_id': inserted_questions[0].question_id,
                      'title': 'updated question title',
                      'allow_multiple': None,
                      'hint': None,
                      'required': None,
                      'logic': None,
                      'type_constraint_name': 'multiple_choice',
                      'choices': [
                          {'old_choice': 'one', 'new_choice': 'two'},
                          {'old_choice': 'one', 'new_choice': 'three'}]}]

        update_json['questions'] = questions
        self.assertRaises(RepeatedChoiceError, api.survey.update, update_json)


    def testDelete(self):
        data = {'title': 'api_test survey'}
        survey_id = api.survey.create(data)['survey_id']
        api.survey.delete(survey_id)
        self.assertRaises(SurveyDoesNotExistError, survey_select, survey_id)


if __name__ == '__main__':
    unittest.main()

