-- Table: logical_constraint

-- DROP TABLE logical_constraint;

CREATE TABLE logical_constraint
(
  logical_constraint_id   uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  logical_constraint_name text UNIQUE NOT NULL,
  -- After discussion with Chris, maybe there should be a json field after all.
  -- It would make things much easier on the server side. After all, the
  -- database doesn't actually care.

  logical_constraint_last_update_time timestamp with time zone NOT NULL
                                      DEFAULT now()

)
WITH (
  OIDS=FALSE
);
ALTER TABLE logical_constraint
  OWNER TO postgres;

-- example question varieties:
-- e-mail
-- age (with limits)
-- checkbox
-- select field 

