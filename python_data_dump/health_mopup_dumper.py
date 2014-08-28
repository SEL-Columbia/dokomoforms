import argparse
import json
import psycopg2 as pg
import urllib2


def bool_to_str(input_bool):
    try:
        answer = 'TRUE' if input_bool.lower() == 'yes' else 'False'
    except AttributeError:
        answer = 'TRUE' if input_bool else 'FALSE'
    return answer

def none_to_zero(input_int):
    return 0 if input_int is None else input_int

def main():
    """Submaximal laziness"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dbname', default='test')
    parser.add_argument('-l', '--host', default='localhost')
    parser.add_argument('-u', '--user', default='postgres')
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-f', '--file_url', required=True)
    args = parser.parse_args()

    con = pg.connect(dbname=args.dbname, host=args.host, user=args.user, password=args.password)
    cursor = con.cursor()

    cursor.execute('delete from survey;')
    cursor.execute('delete from submission;')
    cursor.execute('delete from question_type;')
    cursor.execute('delete from question;')
    cursor.execute('delete from question_choice;')
    cursor.execute('delete from question_branch;')
    cursor.execute('delete from answer;')
    cursor.execute('delete from answer_pick_choice;')
    cursor.execute('delete from answer_checkbox;')
    
    query = "insert into survey (title, survey_owner) values ('health_mopup', 'postgres');"
    cursor.execute(query)

    cursor.execute("select survey_id from survey where title='health_mopup';")
    survey_id = cursor.fetchone()[0]

    query = "insert into question_type (question_type_name) values ('integer'), ('multiple_choice');"
    cursor.execute(query)

    query =  "insert into question (title, sequence_number, question_type_name, survey_id) values "
    query += "('antenatal_care_yn', 0, 'multiple_choice', '{}'),".format(survey_id)
    query += "('num_doctors_fulltime', 1, 'integer', '{}'),".format(survey_id)
    query += "('num_midwives_fulltime', 2, 'integer', '{}'),".format(survey_id)
    query += "('num_nurses_fulltime', 3, 'integer', '{}'),".format(survey_id)
    query += "('num_chews_fulltime', 4, 'integer', '{}'),".format(survey_id)
    query += "('num_toilets_total', 5, 'integer', '{}');".format(survey_id)
    cursor.execute(query)

    cursor.execute("select question_id from question;")
    question_ids = [row[0] for row in cursor.fetchall()]

    query =  "insert into question_choice (choice, choice_number, question_id, question_type_name, question_sequence_number, survey_id) values"
    query += "('yes', 1, '{}', 'multiple_choice', 0, '{}'),".format(question_ids[0], survey_id)
    query += "('no',  2, '{}', 'multiple_choice', 0, '{}'),".format(question_ids[0], survey_id)
    query += "('dk',  3, '{}', 'multiple_choice', 0, '{}');".format(question_ids[0], survey_id)
    cursor.execute(query)

    cursor.execute("select question_choice_id from question_choice;")
    choice_ids = [row[0] for row in cursor.fetchall()]

    def get_choice_id(input_str):
        if input_str == 'yes':
            return choice_ids[0]
        elif input_str == 'no':
            return choice_ids[1]
        elif input_str == 'dk':
            return choice_ids[2]
        else:
            raise Exception('aaaaaa')

    cursor.execute("select question_choice_id from question_choice where choice_number=1")
    choice_id = cursor.fetchone()[0]

    query =  "insert into question_branch (question_choice_id, from_question_id, from_question_type, "
    query += "from_sequence_number, from_survey_id, to_question_id, to_question_type, to_sequence_number, to_survey_id) values "
    query += "('{}', '{}', 'multiple_choice', 0, '{}', '{}', 'integer', 2, '{}');".format(choice_id, question_ids[0], survey_id, question_ids[2], survey_id)
    cursor.execute(query)

    data = json.load(urllib2.urlopen(args.file_url))
    val = data['values']
    for index in xrange(len(val)):
        cursor.execute("insert into submission (latitude, longitude, submitter) values (0, 0, 'postgres{}')".format(index))
        
        cursor.execute("select submission_id from submission where submitter = 'postgres{}'".format(index))
        submission_id = cursor.fetchone()[0]
        
        query = "insert into answer (answer_integer, submission_id, question_id, question_type_name, sequence_number, survey_id) values "
        query += "({}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_doctors_fulltime'][0]), submission_id, question_ids[1], 1, survey_id)
        query += "({}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_midwives_fulltime'][0]), submission_id, question_ids[2], 2, survey_id)
        query += "({}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_nurses_fulltime'][0]), submission_id, question_ids[3], 3, survey_id)
        query += "({}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_chews_fulltime'][0]), submission_id, question_ids[4], 4, survey_id)
        query += "({}, '{}', '{}', 'integer', {}, '{}');".format(none_to_zero(val[index]['num_toilets_total'][0]), submission_id, question_ids[5], 5, survey_id)
        cursor.execute(query)
        
        query =  "insert into answer_pick_choice (question_choice_id, question_id, question_type_name, sequence_number, survey_id, submission_id) values "
        query += "('{}', '{}', 'multiple_choice', 0, '{}', '{}');".format(get_choice_id(val[index]['antenatal_care_yn'][0]), question_ids[0], survey_id, submission_id)
        cursor.execute(query)

    con.commit()

    

if __name__ == '__main__':
    main()

