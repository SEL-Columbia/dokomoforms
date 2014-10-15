-- Table: submission

-- DROP TABLE submission;

CREATE TABLE submission
(
  submission_id    uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  submission_time  timestamp with time zone NOT NULL DEFAULT now(),
  submitter        text                     NOT NULL,

  survey_id        uuid NOT NULL REFERENCES survey ON UPDATE CASCADE
                                                   ON DELETE CASCADE,

  field_update_time timestamp with time zone NOT NULL DEFAULT now(),
  submission_last_update_time timestamp with time zone NOT NULL DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE submission
  OWNER TO postgres;

