from indj_mir.com.indj.mir.utils import DBUtil as du


def insert_data(name, lat, lng, type, address):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO geolocation(name, lat, lng, type, address) VALUES (%s, %s, %s, %s, %s)")
    print('SQL INSERT: ', sql % (name, lat, lng, type, address))

    try:
        # Execute the SQL command
        cursor.execute(sql, (name, lat, lng, type, address))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


def insert_lat_lng_data(lat, lng):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO geolocation(lat, lng) VALUES (%s, %s)")
    print('SQL INSERT: ', sql % (lat, lng))

    try:
        # Execute the SQL command
        cursor.execute(sql, (lat, lng))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


def get_exist_gelocation(lat, lng):
    # Prepare SQL query to get a geolocation by lat and lng geolocation.
    print('lat: ', lat)
    print('lng: ', lng)
    sql = ("SELECT id FROM geolocation AS g WHERE g.lat = %s AND g.lng = %s")
    results = du.execute(sql % (lat, lng))
    return results


def get_all_gelocation():
    # Prepare SQL query to get all geolocations.
    sql = ("SELECT g.lat, g.lng FROM geolocation AS g")
    results = du.execute(sql)
    return results


def update_geolocation_by_group(group_id, lat, lng):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("UPDATE geolocation SET group_id = %s Where lat = %s AND lng = %s")
    print('SQL Update: ', sql % (group_id, lat, lng))

    try:
        # Execute the SQL command
        cursor.execute(sql, (group_id, lat, lng))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()