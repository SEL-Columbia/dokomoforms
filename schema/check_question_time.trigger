-- Function: check_question_time_function()

-- DROP FUNCTION check_question_time_function();

CREATE OR REPLACE FUNCTION check_question_time_function()
  RETURNS trigger AS
$BODY$
DECLARE
    the_question_type text;
begin
  SELECT question_type
    into the_question_type
  FROM question
  WHERE question.id = NEW.question_id;
  IF the_question_type != 'time' THEN
    raise exception 'time questions must have answer_time answers';
  end if;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_question_time_function()
  OWNER TO postgres;

-- Trigger: check_question_time_trigger on answer_time

-- DROP TRIGGER check_question_time_trigger ON answer_time;

CREATE TRIGGER check_question_time_trigger
  BEFORE INSERT OR UPDATE
  ON answer_time
  FOR EACH ROW
  EXECUTE PROCEDURE check_question_time_function();

