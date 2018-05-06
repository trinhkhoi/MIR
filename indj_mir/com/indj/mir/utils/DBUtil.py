import MySQLdb
from django.conf import settings


def init_connection():
    # Open database connection
    config = settings.DATABASES['default']
    db = MySQLdb.connect(config['HOST'], config['USER'],
                         config['PASSWORD'], config['NAME'], charset='utf8', init_command='SET NAMES UTF8')

    return db


def execute(sql):
    # Open database connection
    db = init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    # Execute sql
    cursor.execute(sql)

    results = []
    for item in cursor:
        results.append(item)
    # disconnect from server
    cursor.close()
    db.close()
    return results