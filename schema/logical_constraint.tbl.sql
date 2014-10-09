-- Table: logical_constraint

-- DROP TABLE logical_constraint;

CREATE TABLE logical_constraint
(
  logical_constraint_id   uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  logical_constraint_name text UNIQUE NOT NULL,

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

