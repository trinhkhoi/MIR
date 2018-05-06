from indj_mir.com.indj.mir.utils import DBUtil as du
from datetime import datetime


def insert_data(title, type_screen, condition_uid, data):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO screens(title, type, condition_uid, channel_datas, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)")
    print('SQL INSERT: ', sql % (title, type_screen, condition_uid, data, datetime.now(), datetime.now()))

    try:
        # Execute the SQL command
        cursor.execute(sql, (title, type_screen, condition_uid, data, datetime.now(), datetime.now()))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


# Update channel_datas to screen table by title, type = 'home' and condition_uid
def update_by_title_condition(title, type_screen, condition_uid, data):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("UPDATE screens SET channel_datas = %s WHERE title = %s AND condition_uid = %s AND type = %s")
    print('SQL: ', sql % (data, title, condition_uid, type_screen))
    try:
        # Execute the SQL command
        cursor.execute(sql, (data, title, condition_uid, type_screen))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


# Get exist screen channel by title, type = 'home', and condition_uid
def get_screen_by_title_condition(title, type_screen, condition_uid):
    # Prepare SQL query to get conditions by uid.
    sql = (
        "SELECT COUNT(*) FROM screens WHERE title = '%s' AND condition_uid = %s AND type = '%s'" % (title, condition_uid, type_screen))
    results = du.execute(sql)
    return results