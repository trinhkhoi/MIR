from indj_mir.com.indj.mir.respository import ChannelRepository
from indj_mir.com.indj.mir.utils import CommonUtil
from sklearn.metrics.pairwise import cosine_similarity
from indj_mir.com.indj.mir.respository import RecommendConditionRespository as rs
import operator
from indj_mir.com.indj.mir.respository import ScreenRepository as sc
from indj_mir.com.indj.mir.respository import UserRepository as URespository
from indj_mir.com.indj.mir.respository import ActivitiesRespository as ARespository
from indj_mir.com.indj.mir.respository import TagsRespository
import simplejson as json
from datetime import datetime
import calendar
import h5py
from django.conf import settings
import os
import ast
import time
import math
import requests
import urllib
from bs4 import BeautifulSoup

# Build channel with number of songs have same genre and same artist and same tag
def get_all_channels():
    print('=== Start all channels ===')
    start = time.time()
    songs = ChannelRepository.get_all_song_channel()
    stop = time.time()
    print('all channels - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('all channels - Total time extract: ', stop - start)
    return channels


def get_all_channels_home():
    print('=== Start all channels home ===')
    start = time.time()
    songs = ChannelRepository.get_song_channel_home()
    stop = time.time()
    print('all_channels_home - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('all_channels_home - Total time extract: ', stop - start)
    data_file = h5py.File(settings.CHANNELS_HOME, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end all channels home === ')
    return channels


def get_top_channels_home():
    print('=== Start top channels ===')
    start = time.time()
    songs = ChannelRepository.get_top_channels_home()
    stop = time.time()
    print('top_channels_home - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('top_channels_home - Total time extract: ', stop - start)
    data_file = h5py.File(settings.TOP_CHANNELS_HOME, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end top channel home === ')
    return channels


def get_all_channels_radio():
    print('=== Start all channels radio ===')
    start = time.time()
    songs = ChannelRepository.get_song_channel_radio()
    stop = time.time()
    print('all_channels_radio - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('all_channels_radio - Total time extract: ', stop - start)
    data_file = h5py.File(settings.CHANNELS_RADIO, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end all channels radio === ')
    return channels


def get_top_channels_radio():
    print('=== Start top channels radio ===')
    start = time.time()
    songs = ChannelRepository.get_top_channels_radio()
    stop = time.time()
    print('top_channels_radio - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('top_channels_radio - Total time extract: ', stop - start)
    data_file = h5py.File(settings.TOP_CHANNELS_RADIO, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end top channel radio === ')
    return channels


def get_all_casts():
    print('=== Start all casts ===')
    start = time.time()
    songs = ChannelRepository.get_song_cast()
    stop = time.time()
    print('all casts - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('all casts - Total time extract: ', stop - start)
    data_file = h5py.File(settings.CHANNELS_CAST, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end all casts === ')
    return channels


def get_hot_casts():
    print('=== Start hot casts ===')
    start = time.time()
    songs = ChannelRepository.get_hot_casts()
    stop = time.time()
    print('all_channels_home - Total time get SQL: ', stop - start)
    start = time.time()
    channels = extract_channel_info(songs)
    stop = time.time()
    print('all_channels_home - Total time extract: ', stop - start)
    data_file = h5py.File(settings.TOP_CHANNELS_CAST, 'w')
    data_file.attrs["data"] = str(channels)
    data_file.close()
    print('=== end hot cast === ')
    return channels


def get_top_newest_casts(type_screen, user_uid):
    channels = ChannelRepository.get_top_newest_cast()
    results = []
    for index, (c_uid, c_name) in enumerate(channels):
        channel = {}
        channel['uid'] = c_uid
        channel['sequence'] = index
        channel['channel_name'] = c_name
        results.append(channel)
    json_result = json.dumps(results, ensure_ascii=False, encoding="utf-8")

    save_channel_data('new', type_screen, user_uid, json_result)
    return channels


def extract_channel_info(songs):
    channels = {}
    for (s_uid, genre, artist, c_uid, c_name, c_tags) in songs:
        # Extract song genres
        song_genres = CommonUtil.normalized_type(genre)
        # Extract artists of song
        if artist is None or artist == '':
            artist = 'other'
        song_artists = CommonUtil.normalized_type(artist)
        # Extract song tags
        song_tags = []
        if c_tags is not None:
            channel_tags = eval(c_tags)
            for tag in channel_tags:
                song_tags.append('%s_%s' % (tag['name'].replace('#', ''), tag['uid']))
        # Channel for genres
        map_channel_song_attribute(song_genres, channels, c_uid)
        # Channel for artists
        map_channel_song_attribute(song_artists, channels, c_uid)
        # Channel for tags
        map_channel_song_attribute(song_tags, channels, c_uid)
        if 'channel_tags' not in channels[c_uid]:
            channels[c_uid]['channel_tags'] = song_tags
        else:
            channels[c_uid]['channel_tags'].extend(song_tags)

        if 'name' not in channels[c_uid]:
            channels[c_uid]['name'] = c_name

    return channels


# Map genre, artist and tags for each channel
# Format like: {channel_name:{genre_name: number of songs, artist_name: number of songs, tag_name: number of songs}}
def map_channel_song_attribute(attributes, channels, c_uid):
    for item in attributes:
        if c_uid in channels:
            if item in channels[c_uid]:
                channels[c_uid][item] += 1
            else:
                channels[c_uid].update({item: 1})
        else:
            channels[c_uid] = {item: 1}
        if 'total' not in channels[c_uid]:
            channels[c_uid].update({'total': 0})
        channels[c_uid]['total'] += 1


# Sort a list of channels which are the most suitable channel with conditions
def find_k_suitablest_channel(conditions, channels, k=10):
    channel_rate = {}
    for c_uid in channels:
        total_songs = 0
        for item_condition in conditions:
            if item_condition.strip() != '':
                for attribute in channels[c_uid]:
                    if attribute != 'total' and attribute != 'name' and item_condition in attribute:
                        total_songs += channels[c_uid][attribute]
        channel_rate[c_uid] = float(total_songs) / float(channels[c_uid]['total'])
    # Sort rate of channel by decrease value
    channel_rate = sorted(channel_rate.items(), key=operator.itemgetter(1), reverse=True)

    # Build channel_datas from k first items in channel_rate
    results = []
    for index, (channelUid, rate) in enumerate(channel_rate[:k]):
        channel = {}
        channel['uid'] = channelUid
        channel['sequence'] = index
        channel['channel_name'] = channels[channelUid]['name']
        results.append(channel)
    json_result = json.dumps(results, ensure_ascii=False, encoding="utf-8")
    return json_result


def aggregate_channel_information():
    get_all_channels_home()
    get_top_channels_home()
    get_all_channels_radio()
    get_top_channels_radio()
    get_all_casts()
    get_hot_casts()


def get_user_tags_situation(user_uid):
    u_age_tags = []
    u_situation_tags = []
    u_weather_tags = []
    u_week_day = []
    u_season_tags = []
    u_place_tags = []

    user_location = ARespository.get_user_location(user_uid)
    user_info = URespository.get_user_by_uid(user_uid)[0]
    u_age = -1
    u_gender = 'UNKNOW'

    if len(user_info):
        u_gender = user_info[1]
        if user_info[0] is not None:
            u_age = user_info[0]
            current_date = datetime.now()
            u_age = current_date.year - u_age.year

    # Get predict tags by user's age
    u_age_tags.extend(calculate_predict_tags_by_age(u_age, u_gender))
    print('u_age_tags: ', u_age_tags)

    if len(user_location) > 0:
        user_datetime, timestamp, lat, lng, u_speed = user_location[0]
        datetime_object = datetime.strptime(user_datetime.replace('"', ''), '%Y-%m-%d %H:%M:%S')

        # predict tags from user's location
        start = time.time()
        place_tags, university_places = CommonUtil.calculate_tag_by_places(lat, lng)
        u_place_tags.extend(place_tags)
        stop = time.time()
        print('u_place_tags: ', u_place_tags)
        print('time_place: ', stop - start)

        # predict weather tags based on user's location
        start = time.time()
        u_weather_tags, location_key = CommonUtil.get_weather_by_geolocation(lat, lng)
        stop = time.time()
        print('u_weather_tags: ', u_weather_tags)
        print('time_weather: ', stop - start)

        # predict tags by age and time
        start = time.time()
        u_situation_tags.extend(calculate_action_tag_by_time(datetime_object, u_age, math.ceil(float(u_speed)), university_places))
        stop = time.time()
        print('u_situation_tags: ', u_situation_tags)
        print('time_situation: ', stop - start)

        # get week day of user's date time
        u_week_day.append(calendar.day_name[datetime_object.weekday()])
        print('u_week_day: ', u_week_day)

        # predict season tags by time
        u_season_tags.extend(calculate_season_by_time(datetime_object))
        print('u_season_tags: ', u_season_tags)


    return u_age_tags, u_situation_tags, u_weather_tags, u_week_day, u_season_tags, u_place_tags


def calculate_predict_tags_by_age(u_age, u_gender):
    predict_tags = ''
    if u_age < 20:
        predict_tags = 'young music, edm, pop, hiphop, hip-hop, hip hop, dream, refreshing, refresh, cool, funny, dance, rap, rock, electronic, relax, relaxing, ' \
                       'love, 애정, 젊은 음악, 팝, 힙합, 꿈, 상쾌한, 새롭게 하다, 시원한, 이상한, 댄스, 랩, 록, 전자, 편안한, 개성'
    elif u_age < 39:
        predict_tags = '1990, 2000, young music, pop, edm, relax, relaxing, 젊은 음악, 팝, 편안한'
        if u_gender == 'FEMALE' :
            predict_tags += ', hot, 젝스키스'
        elif u_gender == 'MALE' :
            predict_tags += ', 핑클, SES, 신해철 응답하라 드렁큰타이거'
    else :
        predict_tags = '1990, 김광석, 김현석, 응답하라, 유재하, traditional, 전통적인, bolero, 볼레로, romantic, 낭만적 인'

    return predict_tags.split(',')


def calculate_action_tag_by_time(current_date_time, u_age, u_speed, university_places):
    predict_tags = []
    hourly = []
    for i in range(0, 24):
        hourly.append(current_date_time.replace(hour=i, minute=0, second=0))
        if i == 23:
            hourly.append(current_date_time.replace(hour=i, minute=59, second=59))

    if u_age < 16:
        predict_tags.extend(get_tag_age_16(current_date_time, hourly, u_speed))
    elif u_age >= 16 and u_age < 19:
        predict_tags.extend(get_tag_age_19(current_date_time, hourly, u_speed))
    elif u_age >= 20 and u_age <= 29:
        predict_tags.extend(get_tag_age_29(current_date_time, hourly, u_speed, university_places))
    elif u_age >= 30 and u_age <= 39:
        predict_tags.extend(get_tag_age_39(current_date_time, hourly, u_speed, university_places))

    return predict_tags


def get_tag_age_16(current_date_time, hourly, u_speed):
    predict_tags = []
    if current_date_time >= hourly[5] and current_date_time < hourly[8]:
        if u_speed < 30:
            tags = 'wake up, morning, refreshing, cheerful, light, dawn, exercising, breakfast, 아침 식사, 운동, 일어나, 아침, 상쾌, 청량, 경쾌, 새벽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, go to school, dawn, exercising, morning, refreshing, 운동, 등교길, 새벽, 아침, 운전, 상쾌'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[8] and current_date_time < hourly[10]:
        tags = 'go to school, 등교길, relax, comfortable, relaxing, 편안한'
        predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[10] and current_date_time < hourly[13]:
        if u_speed < 30:
            tags = 'studying, study, reading, windless, comfortable, relax, relaxing, 공부, 독서, 잔잔한, 편안한, 가사없는'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, travel, moving, driving, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[13] and current_date_time < hourly[15]:
        if u_speed < 30:
            tags = 'lunch, afternoon, drowsy, relax, relaxing, 점심, 오후, 나른한, 편안한'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, travel, moving, driving, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))

    elif current_date_time >= hourly[15] and current_date_time < hourly[18]:
        if u_speed < 30:
            tags = 'study, studying, drowsy, relax, relaxing, 공부, 독서, 잔잔한, 가사없는, 나른한, 편안한, 연구'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, travel, moving, driving, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[18] and current_date_time < hourly[20]:
        if u_speed < 30:
            tags = 'hobby, private education, study, reading, relax, relaxing, dinner, 취미, 사교육, 나른한, 편안한, 연구, 공부, 독서, 저녁'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'moving, driving, hobby, 드라이브, 취미'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[20] and current_date_time < hourly[23]:
        if u_speed < 30:
            tags = 'enjoying, gaming, relax, relaxing, 기는, 노름, 편안한'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'moving, driving, hobby, go home, 드라이브, 취미, 집에가'
            predict_tags.extend(tags.split(','))
    else:
        if u_speed < 30:
            tags = 'sleeping, sleep, nap,lullaby, 잠들기전, 잠, 꿀잠, 자장가'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, 밤, drive, moving, 운전, 드라이브'
            predict_tags.extend(tags.split(','))

    return predict_tags


def get_tag_age_19(current_date_time, hourly, u_speed):
    predict_tags = []
    if current_date_time >= hourly[4] and current_date_time < hourly[7]:
        if u_speed < 30:
            tags = 'wake up, morning, refreshing, cheerful, light, dawn, exercising, meditation, 일어나, 아침, 고요, 잔잔, 명상, 아침, 상쾌, 청량, 경쾌, 새벽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, exercising, morning, refreshing, 운동, 등교길, 새벽, 아침, 운전, 상쾌, 청량, 경쾌'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[7] and current_date_time < hourly[9]:
        tags = 'go to school, 등교길, relax, comfortable, relaxing, 편안한'
        predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[9] and current_date_time < hourly[13]:
        if u_speed < 30:
            tags = 'study, studying, reading, instrumental music, windless, relax, relaxing, 공부, 독서, 잔잔한, 편안한, 가사없는'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, moving, drive, driving, travel, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[13] and current_date_time < hourly[15]:
        if u_speed < 30:
            tags = 'lunch, afternoon, 오후, 점심, 나른한'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, moving, drive, driving, 소풍, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[15] and current_date_time < hourly[18]:
        if u_speed < 30:
            tags = 'studying, study, relax, relaxing, 연구,공부하는, 편안한'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'picnic, moving, drive, driving, travel, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[18] and current_date_time < hourly[20]:
        if u_speed < 30:
            tags = 'dinner, relax, relaxing, study, excercising, 저녁, 연구, 공부하는, 편안한, 운동'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'moving, drive, driving, 소풍, 여행, 기분전환, 힐링, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[20] and current_date_time < hourly[22]:
        if u_speed < 30:
            tags = 'self study, relax, relaxing, study, 공부, 독서, 잔잔한, 가사없는, 저녁, 편안한'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, 운전, 드라이브'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[22] and current_date_time <= hourly[24]:
        if u_speed < 30:
            tags = 'studying, relax, relaxing, study, enjoying, night, 공부, 독서, 잔잔한, 가사없는, 저녁, 편안한, 즐기는, 힐링, 휴식, 밤'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, 운전, 드라이브'
            predict_tags.extend(tags.split(','))
    else:
        if u_speed < 30:
            tags = 'sleeping, lullaby, dinner, 잠들기전, 잠, 꿀잠, 자장가, 저녁'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, night, 운전, 드라이브, 퇴근, 밤, 몽환'
            predict_tags.extend(tags.split(','))

    return predict_tags


def get_tag_age_29(current_date_time, hourly, u_speed, university_places):
    predict_tags = []
    if current_date_time >= hourly[5] and current_date_time < hourly[9]:
        if u_speed < 30:
            tags = 'wake up, morning, refreshing, cheerful, light, dawn, exercising, dream, breakfast, 일어나, 아침, 고요, 잔잔, 아침, 상쾌, 청량, 경쾌, 새벽, 몽환, 아침 식사'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, dawn, exercising, morning, refreshing, 운동, 등교길, 새벽, 아침, 운전, 상쾌, 청량, 경쾌'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[9] and current_date_time < hourly[11]:
        tags = 'go to work, go to university, 등교길, 출근'
        predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[11] and current_date_time < hourly[13]:
        if university_places > 1:
            tags = 'study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, 공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, working, concentration, concentrate, 카페, 집중, 작용'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, travel, picnic, 소풍, 여행, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[13] and current_date_time < hourly[15]:
        tags = 'nap, afternoon, lunch, cafe, coffee, 오후, 점심, 나른한, 휴식, 카페, 편집샵'
        predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[15] and current_date_time < hourly[19]:
        if university_places > 1:
            tags = 'study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, 공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, working, concentration, concentrate, 카페, 집중, 작용'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, travel, picnic, 소풍, 여행, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[19] and current_date_time < hourly[22]:
        if university_places > 1:
            tags = 'meeting, study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, 모임, 공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, excercising, 편집샵, 운동, 작용, 위로'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[22] and current_date_time <= hourly[24]:
        if university_places > 1:
            tags = 'calm, cafe, coffee, relax, relaxing, meeting, 위로, 미생, 희망, 잔잔한, 카페, 클럽, 모임'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'meeting, club, bar, cafe, coffee, relax, relaxing, 모임, 편안한, 편집샵, 위로, 클럽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    else:
        if u_speed < 30:
            tags = 'sleep, sleeping, club, bar, 잠들기전, 잠, 꿀잠, 자장가, 위로, 미생, 희망, 클럽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, 기분전환, 힐링, 드라이브, 운전'
            predict_tags.extend(tags.split(','))

    return predict_tags


def get_tag_age_39(current_date_time, hourly, u_speed, university_places):
    predict_tags = []
    if current_date_time >= hourly[5] and current_date_time < hourly[9]:
        if u_speed < 30:
            tags = 'wake up, morning, refreshing, cheerful, light, dawn, calm, windless, exercising, dream, breakfast, meditation,' \
                   ' 일어나, 아침, 고요, 잔잔, 아침, 상쾌, 청량, 경쾌, 새벽, 몽환, 아침 식사, 명상'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, exercising, morning, refreshing, dawn, dream, 운동, 등교길, 새벽, 아침, 운전, 상쾌, 청량, 경쾌, 몽환'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[9] and current_date_time < hourly[11]:
        tags = 'go to work, go to university, 등교길, 출근'
        predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[11] and current_date_time < hourly[13]:
        if university_places > 1:
            tags = 'study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, ' \
                   '공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, working, concentration, concentrate, picnic, travel, mood, lunch, 점심 , 카페, 집중, 작용, 소풍, 여행, 기분전환'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, travel, picnic, 소풍, 여행, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[13] and current_date_time < hourly[15]:
        if u_speed < 30:
            tags = 'nap, afternoon, lunch, cafe, coffee, 오후, 점심, 나른한, 휴식, 카페, 편집샵'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, travel, picnic, 소풍, 여행, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[15] and current_date_time <= hourly[18]:
        if university_places > 1:
            tags = 'study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, ' \
                   '공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, working, concentration, concentrate, 카페, 집중, 작용'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, travel, picnic, 소풍, 여행, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    elif current_date_time > hourly[18] and current_date_time < hourly[21]:
        if university_places > 1:
            tags = 'meeting, study, studying, calm, reading, windless, relax, relaxing, concentration, concentrate, ' \
                   '모임, 공부, 독서, 잔잔한, 편안한, 가사없는, 집중'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'cafe, coffee, excercising, evening, 편집샵, 운동, 작용, 위로, 저녁'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'back to home, driving, drive, moving, 퇴근길, 기분전환, 힐링, 드라이브, 운전, 상쾌, 위로, 희망'
            predict_tags.extend(tags.split(','))
    elif current_date_time >= hourly[21] and current_date_time <= hourly[24]:
        if university_places > 1:
            tags = 'calm, cafe, coffee, relax, relaxing, meeting, 위로, 미생, 희망, 잔잔한, 카페, 클럽, 모임'
            predict_tags.extend(tags.split(','))
        elif u_speed < 30:
            tags = 'meeting, club, bar, cafe, coffee, relax, relaxing, 모임, 편안한, 편집샵, 위로, 클럽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, refreshing, 기분전환, 힐링, 드라이브, 운전, 상쾌, 청량'
            predict_tags.extend(tags.split(','))
    else:
        if u_speed < 30:
            tags = 'sleep, sleeping, club, bar, 잠들기전, 잠, 꿀잠, 자장가, 위로, 미생, 희망, 클럽'
            predict_tags.extend(tags.split(','))
        else:
            tags = 'driving, drive, moving, 기분전환, 힐링, 드라이브, 운전'
            predict_tags.extend(tags.split(','))
    return predict_tags


def calculate_season_by_time(current_date_time):
    predict_tags = []
    if current_date_time.month in (2,3, 4):
        predict_tags.append('spring')
        predict_tags.append('춘추')
    elif current_date_time in (5, 6, 7):
        predict_tags.append('summer')
        predict_tags.append('여름')
    elif current_date_time in (8, 9, 10):
        predict_tags.append('autumn')
        predict_tags.append('fall')
        predict_tags.append('춘추')
        predict_tags.append('가을')
    else:
        predict_tags.append('winter')
        predict_tags.append('겨울')
    return predict_tags


def get_favorite_conditions(user_uid):
    conditions = rs.get_condition_by_user_uid(user_uid)
    lstConditions = set([])
    favorite_tags = []
    favorite_genres = []
    favorite_artists = []
    for (tags, genres, artists, children_genres) in conditions:
        favorite_tags.extend([x.strip() for x in eval(tags)])
        favorite_genres.extend([x.strip() for x in eval(genres)])
        favorite_genres.extend([x.strip() for x in eval(children_genres)])
        favorite_artists.extend([x.strip() for x in eval(artists)])

    lstConditions |= set(favorite_tags)
    lstConditions |= set(favorite_genres)
    lstConditions |= set(favorite_artists)

    return lstConditions, favorite_tags, favorite_genres, favorite_artists


def first_recommend(user_uid):
    starttime = time.time()
    lstConditions, favorite_tags, favorite_genres, favorite_artists = get_favorite_conditions(user_uid)
    u_age_tags, u_situation_tags, u_weather_tags, u_week_day, u_season_tags, u_place_tags = get_user_tags_situation(
        user_uid)

    predict_tags, condition_1, condition_2, condition_3 = get_condition_situation(favorite_tags, favorite_genres, favorite_artists,
                                                                                  u_age_tags, u_situation_tags,
                                                                                  u_weather_tags, u_week_day,
                                                                                  u_season_tags, u_place_tags)
    # Recommend home screen
    recommend_home_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3)
    stoptime = time.time()
    print('***** Total home screen: ', stoptime - starttime)

    # Recommend cast screen
    recommend_cast_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3)

    # Recommend radio screen
    recommend_radio_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3, favorite_tags)


def get_channels_screen(file_path, execute_function):
    print('file path: ', file_path)
    channels = {}
    if not os.path.exists(file_path):
        channels = execute_function
    else:
        with h5py.File(file_path, 'r') as hf:
            channels = ast.literal_eval(hf.attrs["data"])
    return channels


def get_condition_situation(favorite_tags, favorite_genres, favorite_artists, u_age_tags, u_situation_tags, u_weather_tags, u_week_day, u_season_tags, u_place_tags):
    predict_tags = set(u_age_tags)
    predict_tags |= set(u_situation_tags)
    predict_tags |= set(u_weather_tags)
    predict_tags |= set(u_week_day)
    predict_tags |= set(u_season_tags)
    predict_tags |= set(u_place_tags)

    # Get condition for situation 1
    condition_1 = set(favorite_tags)
    condition_1 |= set(favorite_genres)
    condition_1 |= set(favorite_artists)
    condition_1 |= predict_tags
    # Get condition for situation 2
    condition_2 = set(favorite_tags)
    condition_2 |= set(favorite_genres)
    condition_2 |= set(favorite_artists)
    condition_2 |= set(u_weather_tags)
    condition_2 |= set(u_season_tags)
    # Get condition for situation 3
    condition_3 = set(favorite_tags)
    condition_3 |= set(favorite_genres)
    condition_3 |= set(favorite_artists)
    condition_3 |= set(u_weather_tags)
    condition_2 |= set(u_season_tags)
    condition_3 |= set(u_place_tags)

    return predict_tags, condition_1, condition_2, condition_3


def recommend_home_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3):
    # Recommend for home screen
    channels_home = get_channels_screen(settings.CHANNELS_HOME, get_all_channels_home)
    top_channels_home = get_channels_screen(settings.TOP_CHANNELS_HOME, get_top_channels_home)
    recommend_by_screen(lstConditions, 'home', user_uid, channels_home, 'favorite')
    channel_hot_datas = build_json_from_list_channels(top_channels_home)
    save_channel_data('hot', 'home', user_uid, channel_hot_datas)

    # Recommend tags by user's situation
    recommend_tag_situation(predict_tags, 'home', user_uid, channels_home)
    # Recommend channels for situation 1
    recommend_by_screen(condition_1, 'home', user_uid, channels_home, 'situation_1')
    # Recommend channels for situation 2
    recommend_by_screen(condition_2, 'home', user_uid, channels_home, 'situation_2')
    # Recommend channels for situation 3
    recommend_by_screen(condition_3, 'home', user_uid, channels_home, 'situation_3')


def recommend_cast_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3):
    # Recommend for home screen
    channels_cast = get_channels_screen(settings.CHANNELS_CAST, get_all_casts)
    top_channels_cast = get_channels_screen(settings.TOP_CHANNELS_CAST, get_hot_casts)
    recommend_by_screen(lstConditions, 'cast', user_uid, channels_cast, 'favorite')
    cast_hot_datas = build_json_from_list_channels(top_channels_cast)
    save_channel_data('hot', 'cast', user_uid, cast_hot_datas)

    # Recommend tags by user's situation
    recommend_tag_situation(predict_tags, 'cast', user_uid, channels_cast)
    # Get newest casts
    get_top_newest_casts('cast', user_uid)


def recommend_radio_screen(user_uid, lstConditions, predict_tags, condition_1, condition_2, condition_3, favorite_tags):
    # Recommend for home screen
    channels_radio = get_channels_screen(settings.CHANNELS_RADIO, get_all_channels_radio)
    top_channels_radio = get_channels_screen(settings.TOP_CHANNELS_RADIO, get_top_channels_radio)
    recommend_by_screen(lstConditions, 'radio', user_uid, channels_radio, 'favorite')
    radio_hot_datas = build_json_from_list_channels(top_channels_radio)
    save_channel_data('hot', 'radio', user_uid, radio_hot_datas)

    # Recommend tags by user's situation
    #recommend_tag_situation(predict_tags, 'radio', user_uid, channels_radio)
    recommend_by_screen(favorite_tags, 'radio', user_uid, channels_radio, 'tag')
    # Recommend channels for situation 1
    recommend_by_screen(condition_1, 'radio', user_uid, channels_radio, 'situation_1')
    # Recommend channels for situation 2
    recommend_by_screen(condition_2, 'radio', user_uid, channels_radio, 'situation_2')
    # Recommend channels for situation 3
    recommend_by_screen(condition_3, 'radio', user_uid, channels_radio, 'situation_3')


# Calculate tags which will be recommended by situation
def recommend_tag_situation(user_tags, type_screen, user_uid, function_excecute):
    print('recommend_user_tags: ', user_tags)
    recommend_tags = {}

    tags = TagsRespository.get_all_tags()
    for item_condition in user_tags:
        for item_tag in tags:
            if item_condition in item_tag[1]:
                recommend_tags[item_tag[0]] = item_tag[1]

    channels = function_excecute
    for c_uid in channels:
        for attribute in channels[c_uid]['channel_tags']:
            tag_name, tag_uid = attribute.rsplit('_', 1)
            if tag_uid not in recommend_tags:
                recommend_tags[tag_uid] = tag_name

    tag_data = build_json_from_list_channels(recommend_tags, False, k= 20)
    save_channel_data('tag', type_screen, user_uid, tag_data)


# Insert or Update data into screen table
def recommend_by_screen(conditions, type_screen, condition_uid, input_channels, title):
    print('========= Recommend channels by %s =========' % title)
    if len(input_channels) <= 5:
        channels_behavior = build_json_from_list_channels(input_channels)
    else:
        channels_behavior = find_k_suitablest_channel(conditions, input_channels)
    save_channel_data(title, type_screen, condition_uid, channels_behavior)


# Build json of channel_datas if the number of channels <= k
def build_json_from_list_channels(channels, is_channel = True, k = 10):
    results = []
    for index, c_uid in enumerate(channels):
        if index < k:
            channel = {}
            channel['uid'] = c_uid
            channel['sequence'] = index
            if is_channel:
                channel['channel_name'] = channels[c_uid]['name']
            else:
                channel['tag_name'] = channels[c_uid]
            results.append(channel)
        else:
            break
    json_result = json.dumps(results, ensure_ascii=False, encoding="utf-8")
    return json_result


# Insert channel datas into Screen table or update it if the tile and condition already existed
def save_channel_data(title, type_screen, condition_uid, channel_datas):
    screens = sc.get_screen_by_title_condition(title, type_screen, condition_uid)
    if screens[0][0] > 0:
        sc.update_by_title_condition(title, type_screen, condition_uid, channel_datas)
    else:
        sc.insert_data(title, type_screen, condition_uid, channel_datas)


def crawl_channel(start_row):
    channel_titles = ChannelRepository.get_all_channel_title()
    USER_AGENT = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    count = 0
    i = int(start_row)
    for title in channel_titles[int(start_row):]:
        try:
            keyword = ''.join(title)
            print('==== title: ', keyword)

            google_url = 'https://music.bugs.co.kr/search/integrated?q={}'.format(keyword)
            response = requests.get(google_url)
            is_link = parse_search_results(response.text, keyword)
            if is_link:
                count = count + 1
            else:
                file = open('channel_image_not_found.csv', 'a')
                file.write('\n%s' % keyword)
                file.close()
            print('+++++ Index ++++ : ', i)
            print('+++++ Have link ++++ : ', count)
            i += 1
        except Exception as ex:
            print(ex)


def parse_search_results(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')

    is_link = False
    results = soup.body.findAll(text='뮤직PD 앨범')
    print('results: ', results)
    if len(results) > 0:
        result_block = soup.find_all('a', attrs={'class': 'title hyrend'}, href=True)
        is_link = get_channel_link(result_block, keyword)
        if not is_link:
            result_block = soup.find_all('a', attrs={'class': 'albumTitle'}, href=True)
            is_link = get_channel_link(result_block, keyword)
    return is_link


def get_channel_link(result_block, keyword):
    for result in result_block:
        title = result.get_text()
        print('title: ', title)
        if title == keyword:
            print("Found the URL:", result['href'])
            link = result['href']
            get_channel_image(link, keyword)
            return True

    return False


def get_channel_image(link, file_name):
    try:
        response = requests.get(link)
        html_parse = BeautifulSoup(response.text, 'html.parser')
        result_block = html_parse.find_all('span', attrs={'class': 'album'})
        if len(result_block) == 0:
            result_block = html_parse.find_all('li', attrs={'class': 'big'})

        print('Link image: ', result_block)
        for result in result_block:
            link_image = result.find('img')['src']
            with open('%s/%s.jpg' % (settings.PATH_CHANNEL_IMAGE, file_name), "wb") as f:
                f.write(requests.get(link_image).content)
            break
    except Exception as ex:
        file = open('download_image_fail.csv', 'a')
        file.write('\n%s' % file_name)
        file.write('\n%s' % link_image)
        file.close()
        print(str(ex))

def google_scrape(url):
    thepage = urllib.urlopen(url)
    soup = BeautifulSoup(thepage, "html.parser")
    print(soup.title.text)