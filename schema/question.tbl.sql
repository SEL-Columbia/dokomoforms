-- Table: question

-- DROP TABLE question;

CREATE TABLE question
(
  question_id           uuid UNIQUE DEFAULT uuid_generate_v4(),

  title                 text      NOT NULL,
  hint                  text      NOT NULL DEFAULT '',

  -- The sequence number determines the order of the questions in a survey.
  -- Sequence numbers don't have to be consecutive, just unique. Without
  -- branching, the order of the questions goes from lowest sequence number to
  -- highest.
  sequence_number       integer   NOT NULL,

  required              boolean   NOT NULL DEFAULT FALSE,
  -- Set this to true for questions like "list the books available at this
  -- facility."
  allow_multiple        boolean   NOT NULL DEFAULT FALSE,
  type_constraint_name  text REFERENCES type_constraint (type_constraint_name) 
                                                        ON UPDATE CASCADE
                                                        ON DELETE CASCADE,
  logic                 json      NOT NULL DEFAULT '{}',
  survey_id             uuid REFERENCES survey          ON UPDATE CASCADE
                                                        ON DELETE CASCADE,

  question_last_update_time timestamp with time zone NOT NULL DEFAULT now(),

  PRIMARY KEY(question_id,
              type_constraint_name,
              sequence_number,
              allow_multiple,
              survey_id),

  CONSTRAINT question_survey_id_sequence_number_key UNIQUE (survey_id,
                                                            sequence_number),

  CONSTRAINT non_empty_title CHECK (title != '')
)
WITH (
  OIDS=FALSE
);
ALTER TABLE question
  OWNER TO postgres;

