import pandas as pd, numpy as np, time
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
from indj_mir.com.indj.mir.respository import ActivitiesRespository as AcRespository
from indj_mir.com.indj.mir.utils import CommonUtil
from indj_mir.com.indj.mir.respository import GroupGeolocationRepository as GGRespository
from indj_mir.com.indj.mir.respository import GeolocationRepository as GRespository
import os
from django.conf import settings
from xlrd import open_workbook
import simplejson as json

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)


def dbscan_reduce(df, epsilon, x='lon', y='lat'):
    start_time = time.time()
    # represent points consistently as (lat, lon) and convert to radians to fit using haversine metric
    coords = df.as_matrix(columns=[y, x])
    db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    print('Number of clusters: {:,}'.format(num_clusters))

    clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
    print('cluster: ', clusters)

    # find the point in each cluster that is closest to its centroid
    centermost_points = clusters.map(get_centermost_point)

    # unzip the list of centermost points (lat, lon) tuples into separate lat and lon lists
    lats, lons = zip(*centermost_points)
    rep_points = pd.DataFrame({x: lons, y: lats})
    rep_points.tail()

    # pull row from original data set where lat/lon match the lat/lon of each row of representative points
    rs = rep_points.apply(lambda row: df[(df[y] == row[y]) & (df[x] == row[x])].iloc[0], axis=1)

    # all done, print outcome
    message = 'Clustered {:,} points down to {:,} points, for {:.2f}% compression in {:,.2f} seconds.'
    print(message.format(len(df), len(rs), 100 * (1 - float(len(rs)) / len(df)), time.time() - start_time))
    print('RS: ', rs)
    return rs, clusters


def cluster_location():
    # import all new geolocations which are get from activities table
    import_new_geolocation()

    # load the full location history json file downloaded from google
    print('==== Start calculate geolocation cluster ====')
    start = time.time()
    all_geolocations = GRespository.get_all_gelocation()
    array_geolocation = [[float(lat), float(lon)] for lat, lon in all_geolocations]
    matrix_geolocation = np.asmatrix(array_geolocation)

    print('array_geolocation: ', matrix_geolocation)
    d = {'lat': [], 'lon': []}
    df_gps = pd.DataFrame(data=d)
    df_gps['lat'] = pd.Series(float(lat) for (lat, lon) in all_geolocations)
    df_gps['lon'] = pd.Series(float(lon) for (lat, lon) in all_geolocations)

    # define the number of kilometers in one radian
    kms_per_radian = 6371.0088

    # first cluster the full gps location history data set coarsely, with epsilon=5km in radians
    eps_rad = 0.7 / kms_per_radian
    df_clustered, cluster_geolocations = dbscan_reduce(df_gps, epsilon=eps_rad)
    print('Total time dbscan: ', start - time.time())

    print('type result: ', type(df_clustered))
    print('==== Start insert group geolocation to database ====')
    for i in range(len(df_clustered)):
        lat, lng = df_clustered.iloc[i]['lat'], df_clustered.iloc[i]['lon']
        exist_group_geolocation = GGRespository.get_group_by_geolocation(lat, lng)
        if len(exist_group_geolocation) < 1:
            GGRespository.insert_center_lat_lng(lat, lng)
            exist_group_geolocation = GGRespository.get_group_by_geolocation(lat, lng)

        group_geolocations = cluster_geolocations.iloc[i]
        print('group_geolocations: ', group_geolocations)
        for geolocation in group_geolocations:
            print('geolocation: ', geolocation)
            GRespository.update_geolocation_by_group(exist_group_geolocation[0], float(geolocation[0]), float(geolocation[1]))

    # calculate tags for group geolocation
    extract_tag()


def extract_tag():
    print('==== Start calculate tags for each group geolocation ====')
    geolocation_no_tags = GGRespository.get_all_group_gelocation()
    for id, lat, lng in geolocation_no_tags:
        try:
            place_tags, university_places = CommonUtil.calculate_tag_by_places(lat, lng)
            weather_tags, location_key = CommonUtil.get_weather_by_geolocation(lat, lng)
            json_tags = json.dumps(place_tags + weather_tags, ensure_ascii=False, encoding="utf-8")
            GGRespository.update_by_id(id, json_tags, 1 if university_places > 1 else 0, location_key)
        except Exception as ex:
            file = open('error_get_information_geolocation.csv', 'a')
            file.write('\n\nGeolocation: %s - %s ' % (lat, lng))
            file.write('\n%s' % str(ex))
            file.close()


def import_geolocation():
    file_names = os.listdir(settings.INPUT_PATH_GEOLOCATION)

    for item in file_names:
        wb = open_workbook(settings.INPUT_PATH_GEOLOCATION + item)
        print('Load excel file successfully ------- ')

        sheet = wb.sheets()[0]
        number_of_rows = sheet.nrows
        for row in range(1, number_of_rows):
            try:
                name = sheet.cell(row, 0).value
                type = sheet.cell(row, 1).value
                address = sheet.cell(row, 2).value
                lat = sheet.cell(row, 3).value
                lng = sheet.cell(row, 4).value
                if lat is not None and lat != '' and lng is not None and lng != '':
                    exist_geolocation = GRespository.get_exist_gelocation(lat, lng)
                    if len(exist_geolocation) < 1:
                        GRespository.insert_data(name, lat, lng, type, address)
            except Exception as ex:
                file = open('error_import_geolocation.csv', 'a')
                file.write('\n\n%s ' % str(ex))
                file.close()


def import_new_geolocation():
    print('==== Start import geolocation from activities table ====')
    all_geolocations = AcRespository.get_all_geolocation()
    for lat, lng in all_geolocations:
        exist_geolocation = GRespository.get_exist_gelocation(lat, lng)
        if len(exist_geolocation) < 1:
            GRespository.insert_lat_lng_data(lat, lng)