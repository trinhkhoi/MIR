from indj_mir.com.indj.mir.utils import DBUtil as du

def get_all_tags():
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to get all tags.
    sql = ("SELECT uid, name FROM tags")

    cursor.execute(sql)

    print(cursor.rowcount)
    results = []
    for tag_uid, tag_name in cursor:
        results.append([tag_uid, tag_name])
    # disconnect from server
    cursor.close()
    db.close()
    return results