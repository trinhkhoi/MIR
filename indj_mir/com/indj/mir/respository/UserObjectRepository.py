from indj_mir.com.indj.mir.utils import DBUtil as du


def get_all_data():
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, C.uid AS channelUid, JSON_EXTRACT(C.tags, '$[*].name') AS c_tags"
           " FROM songs AS S INNER JOIN channels AS C ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL")

    cursor.execute(sql)

    print(cursor.rowcount)
    results = []
    for channel in cursor:
        results.append(channel)
    # disconnect from server
    cursor.close()
    db.close()
    return results


def get_user_data():
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = (
    "SELECT se.channelUid, re.user_uid, se.songUid,"
       "IF(relation ='like' OR relation = 'follow', 2, 1) AS rating,"
       "se.songArtist,se.songGenre, se.channelTags "
    "FROM relation_user_object AS re "
    "INNER JOIN "
    "(SELECT S.uid AS songUid,"
          "S.name AS songName, S.artist AS songArtist,"
          "S.genre AS songGenre, C.uid AS channelUid,"
          "JSON_UNQUOTE(JSON_EXTRACT(C.tags, '$[*].name')) AS channelTags "
        "FROM songs AS S "
        "LEFT JOIN channels AS C "
        "ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL) AS se "
    "ON re.object_uid = se.songUid "
    "ORDER BY se.channelUid")
    cursor.execute(sql)

    print(cursor.rowcount)
    results = []
    for user in cursor:
        results.append(user)
    # disconnect from server
    cursor.close()
    db.close()
    return results