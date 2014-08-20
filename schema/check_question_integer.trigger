-- Function: check_question_integer_function()

-- DROP FUNCTION check_question_integer_function();

CREATE OR REPLACE FUNCTION check_question_integer_function()
  RETURNS trigger AS
$BODY$
DECLARE
    the_question_type text;
begin
  SELECT question_type
    into the_question_type
  FROM question
  WHERE question.id = NEW.question_id;
  IF the_question_type NOT IN ('integer', 'multiple_choice', 'scale') THEN
    raise exception 'integer, multiple choice, and scale questions must have answer_integer answers';
  end if;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_question_integer_function()
  OWNER TO postgres;

-- Trigger: check_question_integer_trigger on answer_integer

-- DROP TRIGGER check_question_integer_trigger ON answer_integer;

CREATE TRIGGER check_question_integer_trigger
  BEFORE INSERT OR UPDATE
  ON answer_integer
  FOR EACH ROW
  EXECUTE PROCEDURE check_question_integer_function();

