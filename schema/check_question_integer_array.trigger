-- Function: check_question_integer_array_function()

-- DROP FUNCTION check_question_integer_array_function();

CREATE OR REPLACE FUNCTION check_question_integer_array_function()
  RETURNS trigger AS
$BODY$
DECLARE
    the_question_type text;
begin
  SELECT question_type
    into the_question_type
  FROM question
  WHERE question.id = NEW.question_id;
  IF the_question_type != 'checkboxes' THEN
    raise exception 'checkbox questions must have answer_integer_array answers';
  end if;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_question_integer_array_function()
  OWNER TO postgres;

-- Trigger: check_question_integer_array_trigger on answer_integer_array

-- DROP TRIGGER check_question_integer_array_trigger ON answer_integer_array;

CREATE TRIGGER check_question_integer_array_trigger
  BEFORE INSERT OR UPDATE
  ON answer_integer_array
  FOR EACH ROW
  EXECUTE PROCEDURE check_question_integer_array_function();

