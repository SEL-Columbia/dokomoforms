import argparse
import psycopg2 as pg
import urllib2


def main():
    """Submaximal laziness"""

    #Add where clauses everywhere to avoid picking up data from earlier dumps"

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dbname', default='test')
    parser.add_argument('-l', '--host', default='localhost')
    parser.add_argument('-u', '--user', default='postgres')
    parser.add_argument('-p', '--password', required=True)
    args = parser.parse_args()

    con = pg.connect(dbname=args.dbname, host=args.host, user=args.user, password=args.password)
    cursor = con.cursor()

    query = "insert into survey (title, survey_owner) values ('tutorial', 'postgres_tut');"
    cursor.execute(query)

    cursor.execute("select survey_id from survey where title='tutorial';")
    survey_id = cursor.fetchone()[0]

    # Types
    cursor.execute('delete from type_constraint')
    query = "insert into type_constraint (type_constraint_name) values ('integer'), "
            "('multiple_choice'), ('text'), ('multiple_choice_with_other'), ('decimal'), ('date'), ('time');"

    cursor.execute(query)

    # Question styles
    query = "insert into question_variety (question_variety_name) values ('age'), ('scary'), ('spooky_scale'), ('date_picker'), ('colour'); "

    cursor.execute(query)


    # No multiples questions
    query =  "insert into question (title, sequence_number, type_constraint_name, question_variety_name, survey_id) values "
    query += "('Whats your age?', 0, 'integer', 'age', '{}'),".format(survey_id)
    query += "('Whats your favourite colour?', 1, 'multiple_choice', 'colour', '{}'),".format(survey_id)
    query += "('Whats your greatest fear', 2, 'text', 'scary', '{}'),".format(survey_id)
    query += "('Rate your fear between 0 and 1 EXCLUSIVE', 3, 'decimal', 'spooky_scale', '{}'),".format(survey_id)
    query += "('When were you last afraid?', 4, 'date', 'date_picker', '{}'),".format(survey_id)
    query += "('What time exactly?', 5, 'time', NULL, '{}');".format(survey_id)
    cursor.execute(query)

    # XXX: Make some of these branchable 

    # No multiples questions
    query =  "insert into question (title, sequence_number, type_constraint_name, question_variety_name, allow_multiple, survey_id) values "
    query += "('Select your fears and/or fill in your own', 6, 'multiple_choice_with_other', 'scary', true, '{}');".format(survey_id)
    cursor.execute(query)

    
    # get ids for questions
    cursor.execute("select question_id from question;")
    question_ids = [row[0] for row in cursor.fetchall()]

    # colour choices
    query =  "insert into question_choice (choice, choice_number, question_id, allow_multiple, type_constraint_name, question_sequence_number, survey_id) values"
    query += "('red', 1, '{}', false, 'multiple_choice', 1, '{}'),".format(question_ids[1], survey_id)
    query += "('green',  2, '{}', false, 'multiple_choice', 1, '{}'),".format(question_ids[1], survey_id)
    query += "('blue', 3, '{}', false, 'multiple_choice', 1, '{}'),".format(question_ids[1], survey_id)
    query += "('fear',  4, '{}', false, 'multiple_choice', 1, '{}');".format(question_ids[1], survey_id)
    cursor.execute(query)
    
    # fear factors
    query =  "insert into question_choice (choice, choice_number, question_id, allow_multiple, type_constraint_name, question_sequence_number, survey_id) values"
    query += "('clowns', 1, '{}', true, 'multiple_choice_with_other', 6, '{}'),".format(question_ids[6], survey_id)
    query += "('balloons',  2, '{}', true, 'multiple_choice_with_other', 6, '{}'),".format(question_ids[6], survey_id)
    query += "('vijays', 3, '{}', true, 'multiple_choice_with_other', 6, '{}'),".format(question_ids[6], survey_id)
    query += "('fear',  4, '{}', true, 'multiple_choice_with_other', 6, '{}');".format(question_ids[6], survey_id)
    cursor.execute(query)

    # build choice name -> uuid dict
    cursor.execute("select question_choice_id from question_choice;")
    choices = {}
    for row in cursor.fetchall():
        choices[row[1]] = row[0]

    # relic from branching
    #cursor.execute("select question_choice_id from question_choice where choice_number=1")
    #choice_id = cursor.fetchone()[0]

    #query =  "insert into question_branch (question_choice_id, from_question_id,  from_allow_multiple, from_type_constraint, "
    #query += "from_sequence_number, from_survey_id, to_question_id, to_allow_multiple, to_type_constraint, to_sequence_number, to_survey_id) values "
    #query += "('{}', '{}', false, 'multiple_choice', 0, '{}', '{}', false, 'integer', 2, '{}');".format(choice_id, question_ids[0], survey_id, question_ids[2], survey_id)
    #cursor.execute(query)

    for index in xrange(1000):
        cursor.execute("insert into submission (latitude, longitude, submitter) values (0, 0, 'postgres_tut{}')".format(index))
        
        cursor.execute("select submission_id from submission where submitter = 'postgres_tut{}'".format(index))
        submission_id = cursor.fetchone()[0]
        
        query = "insert into answer (answer_integer, submission_id, question_id, allow_multiple, type_constraint_name, sequence_number, survey_id) values "
        query += "({}, '{}', '{}', false, 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_doctors_fulltime'][0]), submission_id, question_ids[1], 1, survey_id)
        query += "({}, '{}', '{}', false, 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_midwives_fulltime'][0]), submission_id, question_ids[2], 2, survey_id)
        query += "({}, '{}', '{}', false, 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_nurses_fulltime'][0]), submission_id, question_ids[3], 3, survey_id)
        query += "({}, '{}', '{}', false, 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_chews_fulltime'][0]), submission_id, question_ids[4], 4, survey_id)
        query += "({}, '{}', '{}', false, 'integer', {}, '{}');".format(none_to_zero(val[index]['num_toilets_total'][0]), submission_id, question_ids[5], 5, survey_id)
        cursor.execute(query)
        
        query =  "insert into answer_choice (question_choice_id, question_id, allow_multiple, type_constraint_name, sequence_number, survey_id, submission_id) values "
        query += "('{}', '{}', false, 'multiple_choice', 0, '{}', '{}');".format(get_choice_id(val[index]['antenatal_care_yn'][0]), question_ids[0], survey_id, submission_id)
        cursor.execute(query)

    con.commit()

    

if __name__ == '__main__':
    main()

