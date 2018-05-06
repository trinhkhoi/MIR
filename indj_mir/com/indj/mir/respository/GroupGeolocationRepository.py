from indj_mir.com.indj.mir.utils import DBUtil as du


def insert_data(lat, long, tags, is_university, location_key):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO group_geolocation(lat, lon, tags, is_university, location_key) VALUES (%s, %s, %s, %s, %s)")
    print('SQL INSERT: ', sql % (lat, long, tags, is_university, location_key))

    try:
        # Execute the SQL command
        cursor.execute(sql, (lat, long, tags, is_university, location_key))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


def insert_center_lat_lng(lat, lng):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = ("INSERT INTO group_geolocation(lat, lon, is_university) VALUES (%s, %s, 0)")
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


# Update tags to group_geolocation table by id
def update_by_id(id, tags, is_university, location_key):
    # Open database connection
    db = du.init_connection()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to update a record into the database.
    sql = ("UPDATE group_geolocation SET tags = %s, is_university = %s, location_key = %s WHERE id = %s")
    print('SQL: ', sql % (tags, is_university, location_key, id))
    try:
        # Execute the SQL command
        cursor.execute(sql, (tags, is_university, location_key, id))
        # Commit your changes in the database
        db.commit()
    except Exception as ex:
        print('Error: ', ex)
        # Rollback in case there is any error
        db.rollback()

    # disconnect from server
    cursor.close()
    db.close()


# Get exist group geolocation by latitude and longitude
def get_group_by_geolocation(lat, lng):
    # Prepare SQL query to get conditions by uid.
    sql = (
        "SELECT id FROM group_geolocation WHERE lat = %s AND lon = %s" % (lat, lng))
    results = du.execute(sql)
    return results


def get_gelocation_no_tag():
    # Prepare SQL query to get all geolocations.
    sql = ("SELECT g.id, g.lat, g.lon FROM group_geolocation AS g WHERE g.tags IS NULL")
    results = du.execute(sql)
    return results


def get_all_group_gelocation():
    # Prepare SQL query to get all geolocations.
    sql = ("SELECT g.id, g.lat, g.lon FROM group_geolocation AS g")
    results = du.execute(sql)
    return results