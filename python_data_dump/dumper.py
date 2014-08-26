import json
import psycopg2 as pg
import sys


def yestrue(input_str):
    return 'TRUE' if (input_str.lower() == 'yes' or input_str.lower() == "true") else 'FALSE'

def none_to_zero(input_str):
    return 0 if input_str == 'null' else int(input_str) #assume integer?

def main():
    """Maximal laziness"""

    pword = sys.argv[1]
    con = pg.connect(dbname='test', host='localhost', user='postgres',
                     password=pword)
    cursor = con.cursor()
    
    query = "insert into survey (title, survey_owner) values ('health_mopup_new', 'postgres'), ('education_mopup_new', 'postgres');"
    cursor.execute(query)

    cursor.execute("select survey_id from survey where title='health_mopup_new';")
    survey_id = cursor.fetchone()[0]

    query = "insert into question_type (question_type_name) values ('boolean');"
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
    

    data = json.load(open('health_mopup_new'))
    val = data['values']
    for index, value in enumerate(something, start=1):
        cursor.execute("insert into submission (latitude, longitude, submitter) values (0, 0, 'postgres{}')".format(index))
        
        cursor.execute("select submission_id from submission where submitter = 'postgres{}'".format(index))
        submission_id = cursor.fetchone()[0]
        
        query = "insert into answer ('answer_{type}', submission_id, question_id, question_type_name, sequence_number, survey_id) values "
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['facility_list_yn'][0]), submission_id, question_ids[0], 1, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'integer', {index}, '{survey_id}'),".format(zero_to_none(val[index-1]['num_doctors_fulltime'][0]), submission_id, question_ids[1], 2, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'integer', {index}, '{survey_id}'),".format(zero_to_none(val[index-1]['num_midwives_fulltime'][0]), submission_id, question_ids[2], 3, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'integer', {index}, '{survey_id}'),".format(zero_to_none(val[index-1]['num_nurses_fulltime'][0]), submission_id, question_ids[3], 4, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'integer', {index}, '{survey_id}'),".format(zero_to_none(val[index-1]['num_chews_fulltime'][0]), submission_id, question_ids[4], 5, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_water_supply.handpump'][0]), submission_id, question_ids[5], 6, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_water_supply.tap'][0]), submission_id, question_ids[6], 7, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_water_supply.protected_well'][0]), submission_id, question_ids[7], 8, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_water_supply.rainwater'][0]), submission_id, question_ids[8], 9, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_water_supply.none'][0]), submission_id, question_ids[9], 10, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_sanitation.vip_latrine'][0]), submission_id, question_ids[10], 11, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_sanitation.pit_latrine_with_slab'][0]), submission_id, question_ids[11], 12, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_sanitation.flush'][0]), submission_id, question_ids[12], 13, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['improved_sanitation.none'][0]), submission_id, question_ids[13], 14, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'integer', {index}, '{survey_id}'),".format(zero_to_none(val[index-1]['num_toilets_total'][0]), submission_id, question_ids[14], 15, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['power_sources.grid'][0]), submission_id, question_ids[15], 16, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['power_sources.solar_system'][0]), submission_id, question_ids[16], 17, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}'),".format(yestrue(val[index-1]['power_sources.generator'][0]), submission_id, question_ids[17], 18, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}');".format(yestrue(val[index-1]['power_sources.none'][0]), submission_id, question_ids[18], 19, survey_id)
        query += "({value}, '{submission_id}', '{question_id}', 'boolean', {index}, '{survey_id}');".format(yestrue(val[index-1]['phcn_electricty'][0]), submission_id, question_ids[19], 20, survey_id)
        cursor.execute(query)

    query = "insert into submission (latitude, longitude, submitter) values (0, 0, 'postgres');"
    cursor.execute(query)

    cursor.execute("select submission_id from submission")
    submission_id = cursor.fetchone()[0]

    query = "insert into answer (answer_boolean, submission_id, ) values ()"

    con.commit()

    

if __name__ == '__main__':
    main()

