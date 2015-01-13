-- Table: survey

-- DROP TABLE survey;

CREATE TABLE survey
(
  survey_id        uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  title            text                     NOT NULL,
  auth_user_id     uuid                     NOT NULL REFERENCES auth_user
                                           ON UPDATE CASCADE ON DELETE CASCADE,
  created_on       timestamp with time zone NOT NULL DEFAULT now(),

  survey_last_update_time timestamp with time zone NOT NULL DEFAULT now(),

  CONSTRAINT survey_title_survey_owner_key UNIQUE (title, auth_user_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE survey
  OWNER TO postgres;

CREATE INDEX survey_id_btree_tpo ON survey(cast(survey_id AS text) text_pattern_ops);
