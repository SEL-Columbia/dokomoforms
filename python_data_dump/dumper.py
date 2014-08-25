import psycopg2 as pg
import sys


def main():
    """Maximal laziness"""

    pword = sys.argv[1]
    con = ph.connect(dbname='test', host='localhost', user='postgres',
                     password=pword)
    cursor = con.cursor()
    query = "insert into survey (title, survey_owner) values ('health_mopup_new', 'postgres');"
    cursor.execute()
    con.commit()

if __name__ == '__main__':
    main()

