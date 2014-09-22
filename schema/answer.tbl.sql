-- Table: answer

-- DROP TABLE answer;

CREATE TABLE answer
(
  answer_id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- These are all the possible answer types... the one that is not NULL is
  -- determined by the CHECK constraint on the type_constraint_name.
  -- Multiple choice answers are in the answer_choice table.
  answer_text          text,
  answer_integer       integer,
  answer_decimal       decimal,
  answer_date          date,
  answer_time          time with time zone,

  question_id          uuid    NOT NULL,
  type_constraint_name text    NOT NULL,
  sequence_number      integer NOT NULL,
  allow_multiple       boolean NOT NULL,
  survey_id            uuid    NOT NULL,
 
  submission_id        uuid    REFERENCES submission ON UPDATE CASCADE
                                                     ON DELETE CASCADE,

  last_update_time     timestamp with time zone NOT NULL DEFAULT now(),

  FOREIGN KEY(question_id,
              type_constraint_name,
              sequence_number,
              allow_multiple,
              survey_id)
    REFERENCES question
             (question_id,
              type_constraint_name,
              sequence_number,
              allow_multiple,
              survey_id)
    ON UPDATE CASCADE ON DELETE CASCADE,

  CONSTRAINT type_constraint_name_matches_answer_type CHECK(
    (CASE WHEN type_constraint_name in ('text', 'multiple_choice_with_other')
                                                  AND answer_text    IS NOT NULL
      THEN 1 ELSE 0 END) +
    (CASE WHEN type_constraint_name =   'integer' AND answer_integer IS NOT NULL
      THEN 1 ELSE 0 END) +
    (CASE WHEN type_constraint_name =   'decimal' AND answer_decimal IS NOT NULL
      THEN 1 ELSE 0 END) +
    (CASE WHEN type_constraint_name =   'date'    AND answer_date    IS NOT NULL
      THEN 1 ELSE 0 END) +
    (CASE WHEN type_constraint_name =   'time'    AND answer_time    IS NOT NULL
      THEN 1 ELSE 0 END)
  = 1),

  CONSTRAINT this_goes_in_another_table CHECK(
    type_constraint_name != 'multiple_choice'
  )
)
WITH (
  OIDS=FALSE
);
CREATE UNIQUE INDEX only_one_answer_allowed
  ON answer (question_id, submission_id)
  WHERE NOT allow_multiple;

ALTER TABLE answer
  OWNER TO postgres;
