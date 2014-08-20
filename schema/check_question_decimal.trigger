-- Function: check_question_decimal_function()

-- DROP FUNCTION check_question_decimal_function();

CREATE OR REPLACE FUNCTION check_question_decimal_function()
  RETURNS trigger AS
$BODY$
DECLARE
    the_question_type text;
begin
  SELECT question_type
    into the_question_type
  FROM question
  WHERE question.id = NEW.question_id;
  IF the_question_type != 'decimal' THEN
    raise exception 'decimal questions must have answer_decimal answers';
  end if;
RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_question_decimal_function()
  OWNER TO postgres;

-- Trigger: check_question_decimal_trigger on answer_decimal

-- DROP TRIGGER check_question_decimal_trigger ON answer_decimal;

CREATE TRIGGER check_question_decimal_trigger
  BEFORE INSERT OR UPDATE
  ON answer_decimal
  FOR EACH ROW
  EXECUTE PROCEDURE check_question_decimal_function();

