from datetime import datetime
from indj_mir.com.indj.mir.utils import DBUtil as du


def insert_data(source_uid, similar_uid, similarity):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO similarity(source_uid, similar_uid, similarity, created_at) VALUES (%s, %s, %s, %s)")
    try:
        # Execute the SQL command
        cursor.execute(sql, (source_uid, similar_uid, similarity, datetime.now()))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    db.close()