from indj_mir.com.indj.mir.utils import DBUtil as du


def get_genres():
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("SELECT DISTINCT genre FROM songs WHERE genre <> ''")
    cursor.execute(sql)

    results = []
    for genre in cursor:
        results.extend(genre)

    # disconnect from server
    cursor.close()
    db.close()

    return results


def get_artists_genres(lst_song_uid):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("SELECT DISTINCT genre, artist FROM songs WHERE uid IN (" + lst_song_uid[0])
    for index in range(1, len(lst_song_uid)):
        print('song_uid: ', lst_song_uid[index])
        sql = sql + (',%s' % lst_song_uid[index])
    sql += ")"
    print('sql: ', sql)
    cursor.execute(sql)

    results = []
    for genre, artist in cursor:
        print('genre: ', genre)
        print('artist: ', artist)
        results.append(genre)
        results.append(artist)

    # disconnect from server
    cursor.close()
    db.close()

    return results