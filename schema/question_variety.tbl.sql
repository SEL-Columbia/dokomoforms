-- Table: question_variety

-- DROP TABLE question_variety;

CREATE TABLE question_variety
(
  question_variety_id   uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_variety_name text UNIQUE,

  last_update_time      timestamp with time zone NOT NULL DEFAULT now()

)
WITH (
  OIDS=FALSE
);
ALTER TABLE question_variety
  OWNER TO postgres;

-- example question varieties:
-- e-mail
-- age (with limits)
-- checkbox
-- select field 

