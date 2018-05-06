from indj_mir.com.indj.mir.utils import DBUtil as du


def get_all_song_channel():
    # Prepare SQL query to get a list of songs which have channel with type = channel or type = cast.
    sql = (
    "SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, C.uid AS channelUid, C.title, C.tags "
    "FROM songs AS S INNER JOIN channels AS C ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL ")
    results = du.execute(sql)
    return results


def get_song_channel_home():
    # Prepare SQL query to get a list of songs which have channel with type = channel or type = cast.
    sql = (
    "SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, C.uid AS channelUid, C.title, C.tags "
    "FROM songs AS S INNER JOIN channels AS C ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL "
    "WHERE C.type = 'channel' OR (C.type = 'cast' AND C.is_live IN ('Y', 'V'))")
    results = du.execute(sql)
    return results

def get_song_channel_radio():
    # Prepare SQL query to get a list of songs which have channel with type = channel.
    sql = (
    "SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, C.uid AS channelUid, C.title, C.tags "
    "FROM songs AS S INNER JOIN channels AS C ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL "
    "WHERE C.type = 'channel'")
    results = du.execute(sql)
    return results

def get_song_cast():
    # Prepare SQL query to get a list of songs which have channel with type = cast.
    sql = (
    "SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, C.uid AS channelUid, C.title, C.tags "
    "FROM songs AS S INNER JOIN channels AS C ON JSON_SEARCH(JSON_EXTRACT(songs, '$[*].uid'), 'one', S.uid) IS NOT NULL "
    "WHERE C.type = 'cast' AND C.is_live IN ('Y', 'V')")
    results = du.execute(sql)
    return results


def get_top_newest_cast(limit = 20):
    # Prepare SQL query to get a list newest channels with type = cast.
    sql = (
    "SELECT C.uid AS channelUid, C.title "
    "FROM channels AS C "
    "WHERE C.type = 'cast' AND C.is_live IN ('Y', 'V') ORDER BY updated_at LIMIT " + str(limit))
    results = du.execute(sql)
    return results


def get_top_channels_home(limit = 50):
    # Prepare SQL query to get top 50 songs which have channel with type = channel or type = cast.
    sql = ("SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, topC.channelUid, topC.title, topC.tags FROM songs AS S "
           "INNER JOIN "
           "(SELECT C.uid AS channelUid, C.title as title, C.tags as tags, JSON_EXTRACT(C.songs, '$[*].uid') AS songUid "
           "FROM channels AS C WHERE played >=0 AND (C.type = 'channel' OR (C.type = 'cast' AND C.is_live IN ('Y', 'V'))) "
           "GROUP BY C.uid ORDER BY played "
           "LIMIT " + str(limit) + ") AS topC "
           "ON JSON_SEARCH(topC.songUid, 'one', S.uid) IS NOT NULL")
    results = du.execute(sql)
    return results


def get_top_channels_radio(limit = 50):
    # Prepare SQL query to get top 50 songs which have channel with type = channel.
    sql = ("SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, topC.channelUid, topC.title, topC.tags FROM songs AS S "
           "INNER JOIN "
           "(SELECT C.uid AS channelUid, C.title as title, C.tags as tags, JSON_EXTRACT(C.songs, '$[*].uid') AS songUid "
           "FROM channels AS C WHERE played >=0 AND C.type = 'channel' "
           "GROUP BY C.uid ORDER BY played "
           "LIMIT " + str(limit) + ") AS topC ON JSON_SEARCH(topC.songUid, 'one', S.uid) IS NOT NULL")
    results = du.execute(sql)
    return results


def get_hot_casts(limit = 50):
    # Prepare SQL query to get top 50 songs which have channel with type = cast.
    sql = ("SELECT S.uid AS songUid, S.genre AS songGenre, S.artist, topC.channelUid, topC.title, topC.tags FROM songs AS S "
           "INNER JOIN "
           "(SELECT C.uid AS channelUid, C.title as title, C.tags as tags, JSON_EXTRACT(C.songs, '$[*].uid') AS songUid "
           "FROM channels AS C WHERE played >=0 AND C.type = 'cast' "
           "GROUP BY C.uid ORDER BY played "
           "LIMIT " + str(limit) + ") AS topC ON JSON_SEARCH(topC.songUid, 'one', S.uid) IS NOT NULL")
    results = du.execute(sql)
    return results


def get_all_channel_title():
    # Prepare SQL for get all channel titles
    sql = ("SELECT title from channels")
    results = du.execute(sql)
    return results

