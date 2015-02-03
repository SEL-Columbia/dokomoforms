-- Table: type_constraint

-- DROP TABLE type_constraint;

CREATE TABLE type_constraint
(
  type_constraint_id   uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  type_constraint_name text UNIQUE NOT NULL,

  type_constraint_last_update_time timestamp with time zone NOT NULL
                                     DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE type_constraint
  OWNER TO postgres;

-- 01 text
-- 02 integer
-- 03 decimal
-- 04 multiple_choice
-- 05 date
-- 06 time
-- 07 location
-- 08 facility
-- 09 note (no answer)
