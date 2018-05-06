from indj_mir.com.indj.mir.utils import DBUtil as du


def get_condition_by_user_uid(user_uid):
    # Prepare SQL query to get conditions by uid.
    sql = (
        "SELECT IFNULL(JSON_EXTRACT(C.conditions, '$.favorites.tags[*].name'),'[]') AS tags, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorites.genres[*].name'),'[]') AS genres, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorites.artists[*].name'),'[]') AS artists, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorites.genres[*].childrens[*].name'),'[]') AS children_genres "
        "FROM recommend_conditions as C WHERE C.user_uid = %s")
    results = du.execute(sql % user_uid)
    return results


def get_all_conditions():
    # Prepare SQL query to get all conditions.
    sql = (
        "SELECT C.uid AS condition_uid, IFNULL(JSON_EXTRACT(C.conditions, '$.channels'),'[]') AS channels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.songs'),'[]') AS songs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.like.song[*].uid'),'[]') AS likesongs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.like.channel[*].uid'),'[]') AS likechannels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.dislike.song[*].uid'),'[]') AS dislikesongs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.dislike.channel[*].uid'),'[]') AS dislikechannels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.tags[*].name'),'[]') AS tags, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.genres[*].name'),'[]') AS genres, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.memberOfArtists[*].artistName'),'[]') AS artists "
        "FROM recommend_conditions as C ")
    results = du.execute(sql)
    return results