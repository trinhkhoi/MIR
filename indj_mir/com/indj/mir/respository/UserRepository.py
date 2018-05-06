from indj_mir.com.indj.mir.utils import DBUtil as du


# Get exist screen channel by title, type = 'home', and condition_uid
def count_all_user():
    # Prepare SQL query to get all users.
    sql = (
        "SELECT COUNT(*) FROM users")
    results = du.execute(sql)
    return results


def get_all_user_conditions():
    # Prepare SQL query to get all user conditions.
    sql = (
        "SELECT U.uid, C.uid AS condition_uid, IFNULL(JSON_EXTRACT(C.conditions, '$.channels'),'[]') AS channels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.songs'),'[]') AS songs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.like.song[*].uid'),'[]') AS likesongs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.like.channel[*].uid'),'[]') AS likechannels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.dislike.song[*].uid'),'[]') AS dislikesongs,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.dislike.channel[*].uid'),'[]') AS dislikechannels,"
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.tags[*].name'),'[]') AS tags, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.genres[*].name'),'[]') AS genres, "
        "IFNULL(JSON_EXTRACT(C.conditions, '$.favorite.memberOfArtists[*].artistName'),'[]') AS artists "
        "FROM users as U INNER JOIN recommend_conditions as C "
        "ON JSON_SEARCH(JSON_EXTRACT(U.info, '$.recommendCondition.uid'), 'one', C.uid) IS NOT NULL ")
    results = du.execute(sql)
    return results


def get_user_by_condition_uid(condition_uid):
    # Prepare SQL query to get users by using condition_uid.
    sql = (
        "SELECT U.uid FROM users as U WHERE U.condition_uid = %s")
    results = du.execute(sql % condition_uid)
    return results


def get_user_by_uid(user_uid):
    sql = "SELECT birthday, gender FROM users WHERE uid = %s"
    results = du.execute(sql % user_uid)
    return results