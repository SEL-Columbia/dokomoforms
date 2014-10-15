DO $$
DECLARE the_auth_user_id uuid;
        the_survey_id    uuid;
BEGIN

INSERT INTO auth_user (email, password)
VALUES ('ebola', 'ebola')
RETURNING auth_user_id INTO the_auth_user_id;

INSERT INTO survey (title, auth_user_id)
VALUES ('Guinea Health Facility Survey', the_auth_user_id)
RETURNING survey_id INTO the_survey_id;

INSERT INTO question (survey_id, sequence_number, title,
type_constraint_name, logical_constraint_name, allow_multiple)
VALUES (the_survey_id, 1, 'What is the location of the facility',
                                                       'location', '', False),
       (the_survey_id, 2, 'What is the bed capacity?', 'integer', '', False),
       (the_survey_id, 3, 'What is the number of new suspected cases?',
                                                       'integer', '', False),
       (the_survey_id, 4, 'What is the number of new confirmed cases?',
                                                       'integer', '', False),
       (the_survey_id, 5, 'What is the number of confirmed deaths?',
                                                       'integer', '', False),
       (the_survey_id, 6,
'What is the number of recovered and released cases?', 'integer', '', False),
       (the_survey_id, 7, 'How many gallons of bleach are there?',
                                                       'integer', '', False),
       (the_survey_id, 8, 'How many boxes of gloves are there?',
                                                       'integer', '', False),
       (the_survey_id, 9, 'How many gloves per box are there?',
                                                       'integer', '', False),
       (the_survey_id, 10, 'How many boxes of face shields are there?',
                                                       'integer', '', False),
       (the_survey_id, 11, 'How many face shields per box are there?',
                                                       'integer', '', False),
       (the_survey_id, 12, 'How many boxes of N95 respirators are there?',
                                                       'integer', '', False),
       (the_survey_id, 13, 'How many N95 respirators per box are there?',
                                                       'integer', '', False),
       (the_survey_id, 14, 'How many boxes of goggles are there?',
                                                       'integer', '', False),
       (the_survey_id, 15, 'How many goggles per box are there?',
                                                       'integer', '', False);

END $$;
