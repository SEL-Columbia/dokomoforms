DO $$
DECLARE the_auth_user_id       uuid;
        the_survey_id          uuid;
        the_from_question_id   uuid;
        the_to_question_id     uuid;
        the_question_choice_id uuid;
BEGIN

INSERT INTO auth_user (email)
VALUES ('test_email')
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
    type_constraint_name, allow_multiple, logic)
VALUES (the_survey_id, 8, 'multiple choice with other question',
           'multiple_choice', False, '{"required": false, "with_other": true}')
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice b', 2, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO auth_user (email)
VALUES ('a.dahir7@gmail.com')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (title, auth_user_id)
VALUES ('test_title2', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'another integer question', 'integer', True),
       (the_survey_id, 5, 'another time question', 'time', True),
       (the_survey_id, 6, 'another location question', 'location', True),
       (the_survey_id, 7, 'another text question', 'text', True),
       (the_survey_id, 9, 'another note', 'note', False);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 2, 'another multiple choice question', 'multiple_choice', 
           False)
RETURNING question_id into the_from_question_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 3, 'another decimal question', 'decimal', True)
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
    False, the_survey_id, the_to_question_id, 'decimal', 3, True,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 4, 'another date question', 'date', True)
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
    False, the_survey_id, the_to_question_id, 'date', 4, True,
    the_survey_id);

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic)
VALUES (the_survey_id, 8, 'another multiple choice with other question',
           'multiple_choice', False, '{"required": false, "with_other": true}')
RETURNING question_id into the_from_question_id;

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice a', 1, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO question_choice (choice, choice_number, question_id,
    type_constraint_name, question_sequence_number, allow_multiple, survey_id)
VALUES ('choice b', 2, the_from_question_id, 'multiple_choice', 8,
    False, the_survey_id);

INSERT INTO survey (title, auth_user_id)
VALUES ('what is life', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic)
VALUES (the_survey_id, 1, 'life', 'integer', False, '{"required": true, "with_other": false}'),
       (the_survey_id, 2, 'there is none fool', 'note', False, '{"required": false, "with_other": false}');

INSERT INTO survey (title, auth_user_id)
VALUES ('what is death', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic)
VALUES (the_survey_id, 1, 'death', 'integer', False, '{"required": true, "with_other": false}'),
       (the_survey_id, 2, 'me', 'note', False, '{"required": false, "with_other": false}');

INSERT INTO survey (title, auth_user_id)
VALUES ('happiness', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple, logic)
VALUES (the_survey_id, 1, 'rate me', 'integer', False, '{"required": true, "with_other": false}'),
       (the_survey_id, 3, 'Tell me how you feel', 'text', True, '{"required": true,"with_other": false }'),
       (the_survey_id, 2, 'thanks, youre the best', 'note', False, '{"required": false, "with_other": false}');

INSERT INTO survey (title, auth_user_id)
VALUES ('do you like me?', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'rate me', 'integer', True),
       (the_survey_id, 2, 'will you go out with me?', 'text', True),
       (the_survey_id, 3, 'im gonan ask you out anyway', 'note', False);

INSERT INTO survey (title, auth_user_id)
VALUES ('my favourite number', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'guess it', 'integer', True),
       (the_survey_id, 2, 'it was 7 btw', 'note', False),
       (the_survey_id, 3, 'also where are you', 'location', False);

INSERT INTO survey (title, auth_user_id)
VALUES ('sadness', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'rat3e life', 'integer', False),
       (the_survey_id, 3, 'it wasnt', 'note', False),
       (the_survey_id, 2, 'was it really worth it', 'text', True);

INSERT INTO survey (title, auth_user_id)
VALUES ('days of the week', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'how many', 'integer', False),
       (the_survey_id, 2, 'but how bout on the moon?', 'note', False);

INSERT INTO survey (title, auth_user_id)
VALUES ('days of the month', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'guess it', 'integer', False),
       (the_survey_id, 2, 'HA', 'note', False);

INSERT INTO survey (title, auth_user_id)
VALUES ('how many pieces of rope to reach the moon', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
    type_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'guess it', 'integer', False),
       (the_survey_id, 2, 'one, if its long enough', 'note', False);
END $$;
