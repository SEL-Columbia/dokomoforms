-- Table: auth_user

-- DROP TABLE auth_user;

CREATE TABLE auth_user
(
  auth_user_id     uuid PRIMARY KEY DEFAULT uuid_generate_v4(),

  email            text UNIQUE NOT NULL,
  token            text UNIQUE NOT NULL DEFAULT CAST(uuid_generate_v4() AS TEXT),
  expires_on       timestamp with time zone NOT NULL DEFAULT now(),

  auth_user_last_update_time timestamp with time zone NOT NULL DEFAULT now()

)
WITH (
  OIDS=FALSE
);
ALTER TABLE auth_user
  OWNER TO postgres;
