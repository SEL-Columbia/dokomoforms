DO $$
DECLARE the_auth_user_id       uuid;
        the_survey_id          uuid;
        the_from_question_id   uuid;
        the_to_question_id     uuid;
        the_question_choice_id uuid;
BEGIN

INSERT INTO auth_user (email, password)
VALUES ('test_email', 'test_password')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (title, auth_user_id)
VALUES ('test_title', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'integer question', 'integer', False),
       (the_survey_id, 5, 'time question', 'time', False),
       (the_survey_id, 6, 'location question', 'location', False),
       (the_survey_id, 7, 'text question', 'text', True),
       (the_survey_id, 9, 'note', 'note', False);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 2, 'multiple choice question', 'multiple_choice', 
           False)
RETURNING question_id into the_from_question_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 3, 'decimal question', 'decimal', False)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 1', 1, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'decimal', 3, False,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 4, 'date question', 'date', False)
RETURNING question_id into the_to_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice 2', 2, the_from_question_id, 'multiple_choice', 2, False,
    the_survey_id)
RETURNING question_choice_id into the_question_choice_id;

INSERT INTO question_branch (question_choice_id, from_question_id,
    from_type_constraint, from_sequence_number, from_allow_multiple,
    from_survey_id, to_question_id, to_type_constraint, to_sequence_number,
    to_allow_multiple, to_survey_id)
VALUES (the_question_choice_id, the_from_question_id, 'multiple_choice', 2,
    False, the_survey_id, the_to_question_id, 'date', 4, False,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 8, 'multiple choice with other question',
           'multiple_choice_with_other', False)
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice_with_other', 8,
    False, the_survey_id);

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice b', 2, the_from_question_id, 'multiple_choice_with_other', 8,
    False, the_survey_id);

END $$;
