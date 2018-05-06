from indj_mir.com.indj.mir.respository import UserObjectRepository
from indj_mir.com.indj.mir.utils import CommonUtil
from indj_mir.com.indj.mir.services import ChannelService


def get_user_data():
    user_ratings = UserObjectRepository.get_user_data()
    user_rating_Dict = {}
    attributes = set([])

    for (channelUid, user_uid, songUid, rating, songArtist, songGenre, channelTags) in user_ratings:
        # Process channel genres
        song_genre = CommonUtil.normalized_type(songGenre)
        attributes |= song_genre
        map_user_attribute(user_rating_Dict, user_uid, song_genre, rating)

        # Process channel artist
        if songArtist is None or songArtist == '':
            songArtist = 'other'

        song_artist = CommonUtil.normalized_type(songArtist)
        attributes |= song_artist
        map_user_attribute(user_rating_Dict, user_uid, song_artist, rating)

        # Process channel tags
        if channelTags is not None:
            print(len(eval(channelTags)))
            #channelTags = channelTags.decode("utf-8")
            print((channelTags))
            tag_channel = CommonUtil.normalized_string(eval(channelTags.replace('#', '')))
            attributes |= tag_channel

            map_user_attribute(user_rating_Dict, user_uid, tag_channel, rating)

    print('attributes: ', attributes)
    remove_duplicated_attribute(user_rating_Dict)

    return sorted(attributes), user_rating_Dict


# Remove genres or artists or tags which are duplicated in both like and dislike set
def remove_duplicated_attribute(user_rating_Dict):
    for key in user_rating_Dict:
        # Remove duplicate attribute in like or dislike list
        user_rating_Dict[key][0] = set(user_rating_Dict[key][0])
        user_rating_Dict[key][1] = set(user_rating_Dict[key][1])
        # Remove genres or artists or tags which are duplicated in both like and dislike set
        [x.remove(du) for du in [elem for elem in user_rating_Dict[key][0] if elem in user_rating_Dict[key][1]] for x in
         user_rating_Dict[key]]
        print(key, user_rating_Dict[key])


# Make a user's dictionary which this user like  or dislike genre, tag, or artist
def map_user_attribute(user_rating_Dict, user_uid, attribute, rating):
    if user_uid in user_rating_Dict:
        if rating == 2:
            user_rating_Dict[user_uid][0].extend(list(attribute))
        else:
            user_rating_Dict[user_uid][1].extend(list(attribute))
    else:
        user_rating_Dict[user_uid] = []
        if rating == 2:
            user_rating_Dict[user_uid].append(list(attribute))
            user_rating_Dict[user_uid].append([])
        else:
            user_rating_Dict[user_uid].append([])
            user_rating_Dict[user_uid].append(list(attribute))


def calculate_user_channel_rating():
    attributes, user_rating_Dict = get_user_data()
    channels = ChannelService.get_all_channels_home()
    for c in channels:
        for user_uid in user_rating_Dict:
            total_like = 0
            total_dislike = 0
            for item in user_rating_Dict[user_uid][0]:
                if item in channels[c]:
                    total_like = total_like + channels[c][item]
            for item in user_rating_Dict[user_uid][1]:
                if item in channels[c]:
                    total_dislike = total_dislike + channels[c][item]



def create_matrix_user():
    attributes, user_rating_Dict = get_user_data()

    keylist = sorted(user_rating_Dict.keys())
    print('len attribute: ', len(attributes))
    print('len user genre: ', len(user_rating_Dict))

    matrix_user_attribute = [[0 for x in range(len(attributes))] for y in range(len(keylist))]
    matrix_rate = []
    file = open('data.dat', 'w')
    flag = True
    for i, key in enumerate(keylist):
        print(i, ': ', key)
        for j, attribute in enumerate(attributes):
            if flag:
                print(j, ': ', attribute)
            if attribute in user_rating_Dict[key][0]:
                matrix_user_attribute[i][j] = 2
                matrix_rate.append([i, j, 2])
                if i == 0 and j == 0:
                    file.write('%s %s %s.' % (i, j, 4))
                else:
                    file.write('\n%s %s %s.' % (i, j, 4))
            elif attribute in user_rating_Dict[key][1]:
                matrix_user_attribute[i][j] = 1
                matrix_rate.append([i, j, 1])
                if i == 0 and j == 0:
                    file.write('%s %s %s.' % (i, j, 1))
                else:
                    file.write('\n%s %s %s.' % (i, j, 1))

        if flag:
            flag = False
    file.close()

    return keylist


