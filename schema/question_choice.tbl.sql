-- Table: question_choice

-- DROP TABLE question_choice;

CREATE TABLE question_choice
(
  question_choice_id       uuid UNIQUE DEFAULT uuid_generate_v4(),

  choice                   text    NOT NULL,
  choice_number            integer NOT NULL,

  question_id              uuid    NOT NULL,
  type_constraint_name     text    NOT NULL,
  question_sequence_number integer NOT NULL,
  allow_multiple           boolean NOT NULL,
  survey_id                uuid    NOT NULL,

  question_choice_last_update_time timestamp with time zone NOT NULL
                                     DEFAULT now(),

  PRIMARY KEY(question_choice_id,
              question_id,
              type_constraint_name,
              question_sequence_number,
              allow_multiple,
              survey_id),

  FOREIGN KEY(question_id,
              type_constraint_name,
              question_sequence_number,
              allow_multiple,
              survey_id)
    REFERENCES question
             (question_id,
              type_constraint_name,
              sequence_number,
              allow_multiple,
              survey_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
 
  -- A question can't have multiples of the same choice number. 
  CONSTRAINT question_choice_question_id_choice_number_key
    UNIQUE (question_id, choice_number),
  CONSTRAINT question_should_have_choices CHECK(
    type_constraint_name IN ('multiple_choice', 'multiple_choice_with_other')
  )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE question
  OWNER TO postgres;

