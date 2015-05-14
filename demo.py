#! /usr/bin/env python3

from dokomoforms import db
from dokomoforms.api.user import create_user
from dokomoforms.api.survey import create as create_survey

connection = db.engine.connect()


def main():
    with connection.begin():
        create_user(connection, {'email': 'dokomoforms.demo@gmail.com'})
        create_survey(
            connection,
            {
                'survey_title': 'Demo School Survey',
                'email': 'dokomoforms.demo@gmail.com',
                'questions': [
                    {
                        'question_title': 'How many students are there?',
                        'hint': 'You know, pupils.',
                        'logic': {
                            'required': False,
                            'allow_dont_know': True,
                            'allow_other': False,
                        },
                        'type_constraint_name': 'integer',
                        'sequence_number': 1,
                        'allow_multiple': False,
                        'question_to_sequence_number': 2,
                        'choices': None,
                        'branches': None,
                    },
                    {
                        'question_title': 'Which kind of school is this?',
                        'hint': None,
                        'logic': {
                            'required': False,
                            'allow_dont_know': False,
                            'allow_other': True,
                        },
                        'type_constraint_name': 'multiple_choice',
                        'sequence_number': 2,
                        'allow_multiple': False,
                        'question_to_sequence_number': 3,
                        'choices': ['Elementary', 'Middle', 'High'],
                        'branches': None,
                    },
                    {
                        'question_title': "What's the average test score?",
                        'hint': None,
                        'logic': {
                            'required': False,
                            'allow_dont_know': True,
                            'allow_other': False,
                        },
                        'type_constraint_name': 'decimal',
                        'sequence_number': 3,
                        'allow_multiple': False,
                        'question_to_sequence_number': -1,
                        'choices': None,
                        'branches': None,
                    },
                ],
                'survey_metadata': {
                    'author': 'Sel Columbia',
                    'organization': 'SEL',
                    'location': {"lon": 5.118915, "lat": 7.353078},
                },
            },
        )


if __name__ == '__main__':
    main()
