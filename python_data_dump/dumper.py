import argparse
import json
import psycopg2 as pg


def bool_to_str(input_bool):
    return 'TRUE' if input_bool else 'FALSE'

def none_to_zero(input_int):
    return 0 if input_int is None else input_int

def main():
    """Submaximal laziness"""

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', 'dbname', default='test')
    parser.add_argument('-h', 'host', default='localhost')
    parser.add_argument('-u', 'user', default='postgres')
    parser.add_argument('-p', 'password')
    parser.add_argument('-f', 'file_path')
    parser.add_argument('-s', 'survey_name')
    args = parser.parse_args()

    con = pg.connect(dbname=args.dbname, host=args.host, user=args.user, password=args.password)
    cursor = con.cursor()
    
    query = "insert into survey (title, survey_owner) values ('{}', 'postgres');".format(args.survey_name)
    cursor.execute(query)

    cursor.execute("select survey_id from survey;")
    survey_id = cursor.fetchone()[0]

    query = "insert into question_type (question_type_name) values ('boolean'), ('integer');"
    cursor.execute(query)

    query =  "insert into question (title, sequence_number, question_type_name, survey_id) values "
    query += "('facility_list_yn', 1, 'boolean', '{0}'),"
    query += "('num_doctors_fulltime', 2, 'integer', '{0}'),"
    query += "('num_midwives_fulltime', 3, 'integer', '{0}'),"
    query += "('num_nurses_fulltime', 4, 'integer', '{0}'),"
    query += "('num_chews_fulltime', 5, 'integer', '{0}'),"
    query += "('improved_water_supply.handpump', 6, 'boolean', '{0}'),"
    query += "('improved_water_supply.tap', 7, 'boolean', '{0}'),"
    query += "('improved_water_supply.protected_well', 8, 'boolean', '{0}'),"
    query += "('improved_water_supply.rainwater', 9, 'boolean', '{0}'),"
    query += "('improved_water_supply.none', 10, 'boolean', '{0}'),"
    query += "('improved_sanitation.vip_latrine', 11, 'boolean', '{0}'),"
    query += "('improved_sanitation.pit_latrine_with_slab', 12, 'boolean', '{0}'),"
    query += "('improved_sanitation.flush', 13, 'boolean', '{0}'),"
    query += "('improved_sanitation.none', 14, 'boolean', '{0}'),"
    query += "('num_toilets_total', 15, 'integer', '{0}'),"
    query += "('power_sources.grid', 16, 'boolean', '{0}'),"
    query += "('power_sources.solar_system', 17, 'boolean', '{0}'),"
    query += "('power_sources.generator', 18, 'boolean', '{0}'),"
    query += "('power_sources.none', 19, 'boolean', '{0}'),"
    query += "('phcn_electricity', 20, 'boolean', '{0}');"
    query.format(survey_id)
    cursor.execute(query)

    cursor.execute("select question_id from question;")
    question_ids = [row[0] for row in cursor.fetchall()]
    

    data = json.load(open(SOMETHING))
    val = data['values']
    for index in xrange(len(val)):
        cursor.execute("insert into submission (latitude, longitude, submitter) values (0, 0, 'postgres{}')".format(index))
        
        cursor.execute("select submission_id from submission where submitter = 'postgres{}'".format(index))
        submission_id = cursor.fetchone()[0]
        
        query = "insert into answer (answer_boolean, answer_integer, submission_id, question_id, question_type_name, sequence_number, survey_id) values "
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['facility_list_yn'][0]), submission_id, question_ids[0], 1, survey_id)
        query += "(NULL, {}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_doctors_fulltime'][0]), submission_id, question_ids[1], 2, survey_id)
        query += "(NULL, {}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_midwives_fulltime'][0]), submission_id, question_ids[2], 3, survey_id)
        query += "(NULL, {}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_nurses_fulltime'][0]), submission_id, question_ids[3], 4, survey_id)
        query += "(NULL, {}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_chews_fulltime'][0]), submission_id, question_ids[4], 5, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_water_supply.handpump'][0]), submission_id, question_ids[5], 6, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_water_supply.tap'][0]), submission_id, question_ids[6], 7, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_water_supply.protected_well'][0]), submission_id, question_ids[7], 8, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_water_supply.rainwater'][0]), submission_id, question_ids[8], 9, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_water_supply.none'][0]), submission_id, question_ids[9], 10, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_sanitation.vip_latrine'][0]), submission_id, question_ids[10], 11, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_sanitation.pit_latrine_with_slab'][0]), submission_id, question_ids[11], 12, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_sanitation.flush'][0]), submission_id, question_ids[12], 13, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['improved_sanitation.none'][0]), submission_id, question_ids[13], 14, survey_id)
        query += "(NULL, {}, '{}', '{}', 'integer', {}, '{}'),".format(none_to_zero(val[index]['num_toilets_total'][0]), submission_id, question_ids[14], 15, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['power_sources.grid'][0]), submission_id, question_ids[15], 16, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['power_sources.solar_system'][0]), submission_id, question_ids[16], 17, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['power_sources.generator'][0]), submission_id, question_ids[17], 18, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}'),".format(bool_to_str(val[index]['power_sources.none'][0]), submission_id, question_ids[18], 19, survey_id)
        query += "({}, NULL, '{}', '{}', 'boolean', {}, '{}');".format(bool_to_str(val[index]['phcn_electricty'][0]), submission_id, question_ids[19], 20, survey_id)
        cursor.execute(query)

    con.commit()

    

if __name__ == '__main__':
    main()

