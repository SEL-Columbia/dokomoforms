-- Table: answer_choice

-- DROP TABLE answer_choice;

CREATE TABLE answer_choice
(
  answer_choice_id        uuid    PRIMARY KEY DEFAULT uuid_generate_v4(),

  question_choice_id      uuid    NOT NULL,

  question_id             uuid    NOT NULL,
  type_constraint_name    text    NOT NULL,
  sequence_number         integer NOT NULL,
  allow_multiple          boolean NOT NULL,
  survey_id               uuid    NOT NULL,

  submission_id           uuid    REFERENCES submission ON UPDATE CASCADE
                                                        ON DELETE CASCADE,

  last_update_time        timestamp with time zone NOT NULL DEFAULT now(),

  FOREIGN KEY(question_choice_id,
              question_id,
              type_constraint_name,
              sequence_number,
              allow_multiple,
              survey_id)
                         REFERENCES question_choice
             (question_choice_id,
              question_id,
              type_constraint_name,
              question_sequence_number,
              allow_multiple,
              survey_id) ON UPDATE CASCADE ON DELETE CASCADE,

  UNIQUE(question_choice_id, submission_id),

  CONSTRAINT multiple_choice_answer_type_matches CHECK(
    type_constraint_name IN ('multiple_choice', 'multiple_choice_with_other')
  )
)
WITH (
  OIDS=FALSE
);
CREATE UNIQUE INDEX only_one_choice_allowed
  ON answer_choice (submission_id, question_id)
  WHERE NOT allow_multiple;

ALTER TABLE answer
  OWNER TO postgres;

