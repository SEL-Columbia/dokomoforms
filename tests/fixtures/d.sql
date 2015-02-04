DO $$
DECLARE the_auth_user_id uuid;
        the_survey_id    uuid;
BEGIN

INSERT INTO auth_user (email)
VALUES ('vr2262@columbia.edu')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (survey_title, auth_user_id)
VALUES ('Demonstration Survey', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, question_title,
  type_constraint_name, allow_multiple, question_to_sequence_number)
VALUES (the_survey_id, 1, 'What is the best number?', 'integer', False, 2),
       (the_survey_id, 2, 'What should we call this software?', 'text', False, 3),
       (the_survey_id, 3, 'What is your location?', 'location', False, -1);
END $$;
