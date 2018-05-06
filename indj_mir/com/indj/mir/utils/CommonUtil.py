import nltk
from nltk.corpus import wordnet
from googletrans import Translator
import simplejson as json
import requests
import forecastio

GENRE_DICT = {"발라드": "ballade", "재즈": "jazz", "클래식": "classic", "힙합": "hiphop", "일렉트로닉": "edm", "electronic": "edm",
              "팝": "pop", "디스코": "disco", "펑크": "punk", "훵크": "funk", "월드": "world", "컨트리": "country", "씨씨엠": "ccm",
              "인디": "indie", "알엔비": "rnb", "락": "rock", "종교": "religion", "기타": "etc", "rhythm & blues": "r&b",
              "electronica": "edm"}


def normalized_type_unique(input):
    input = input.lower()
    if '/' not in input and ',' not in input:
        if '-' in input:
            input = input.replace('-', '')
        if '(' in input:
            input = input[input.find('(')+1:input.find(')')]
        if input in GENRE_DICT:
            input = GENRE_DICT[input]
        return set([input.strip()])
    else:
        results = set([])
        s_split = '/'
        if ',' in input:
            s_split = ','
        splitItems = [x.strip() for x in input.split(s_split)]
        results |= normalized_string_unique(splitItems)
        return results


def normalized_string_unique(s):
    uniqueString = set([])
    for sItem in s:
        item = sItem
        if '(' in item:
            item = item[item.find("(")+1:item.find(")")]
        if '-' in item:
            item = item.replace('-', '')
        if item in GENRE_DICT:
            item = GENRE_DICT[item]
        uniqueString.add(item)
    return uniqueString


def normalized_type(input):
    if input is None:
        return []
    input = input.lower()
    if '/' not in input and ',' not in input:
        if '-' in input:
            input = input.replace('-', '')
        if '(' in input:
            input = input[input.find('(')+1:input.find(')')]
        if input in GENRE_DICT:
            input = GENRE_DICT[input]
        return [input.strip()]
    else:
        results = []
        s_split = '/'
        if ',' in input:
            s_split = ','
        splitItems = [x.strip() for x in input.split(s_split)]
        results.extend(normalized_string(splitItems))
        return results


def normalized_string(s):
    uniqueString = []
    for sItem in s:
        item = sItem
        if '(' in item:
            item = item[item.find("(")+1:item.find(")")]
        if '-' in item:
            item = item.replace('-', '')
        if item in GENRE_DICT:
            item = GENRE_DICT[item]
        uniqueString.append(item)
    return uniqueString


def normalized_tag(tag_uid, tag_name):
    item = tag_name
    if '(' in tag_name:
        item = tag_name[tag_name.find("(") + 1:tag_name.find(")")]
    if '-' in tag_name:
        item = tag_name.replace('-', '')
    if tag_name in GENRE_DICT:
        item = GENRE_DICT[tag_name]
    return '%s_%s' % (item, tag_uid)


def get_synonym_words(lst_origin_words):
    synonyms = []
    for origin_word in lst_origin_words:
        for syn in wordnet.synsets(origin_word):
            for l in syn.lemmas():
                synonyms.append(l.name())

    return translate_En_to_Ko(set(synonyms))


def translate_En_to_Ko(lst_keywords):
    translator = Translator()
    ko_keywords = []
    for en_word in lst_keywords:
        if '_' in en_word:
            en_word = en_word.replace('_', ' ')
        ko_keywords.append(en_word)
        ko_keywords.append(translator.translate(en_word, 'ko').text)

    print('ko_keywords: ', ko_keywords)
    return ko_keywords


def calculate_tag_by_places(lat,lng):
    predict_tags = []

    lakePlaces = get_near_places(lat, lng, 'lake')
    riverPlaces = get_near_places(lat, lng, 'river')
    if lakePlaces > 1 or riverPlaces > 1:
        tags = 'lake, river, 호수, 강'
        predict_tags.extend([x.strip() for x in tags.split(',')])
    if len(predict_tags) == 0:
        beachPlaces = get_near_places(lat, lng, 'beach')
        if beachPlaces > 1:
            tags = 'beach, sea, ocean, 바닷가, 바다, 대양'
            predict_tags.extend([x.strip() for x in tags.split(',')])
    if len(predict_tags) == 0:
        mountainPlaces = get_near_places(lat, lng, 'mountain')
        if mountainPlaces > 1:
            tags = 'mountain, hill, hilly, pap, gorge, 산, 언덕, 산이 많은, 어린애 속임수, 협곡'
            predict_tags.extend([x.strip() for x in tags.split(',')])
    universityPlaces = 0
    if len(predict_tags) == 0:
        universityPlaces = get_near_places(lat, lng, 'university')

    return predict_tags, universityPlaces


def get_near_places(lat, lon, keyword):
    API_KEY = 'API_KEY'
    URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=700&keyword=%s&key=%s'

    # get place with near lake
    r = requests.get(URL % (lat, lon, keyword, API_KEY))
    # convert to Json format
    data = json.loads(r.text)

    return len(data['results'])


def get_weather_by_geolocation(lat, lng):
    #API_KEY = '8db435f5c7dcfeb392c95245364e99b3'
    #forecast = forecastio.load_forecast(API_KEY, lat, lng)
    # current_weather = forecast.currently()
    # temprature = (current_weather.temperature - 32) * 5.0/9.0
    API_KEY = 'API_KEY'
    URL_LOCATION_KEY = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=%s&q=%s,%s'
    URL_CURRENT_WEATHER = 'http://dataservice.accuweather.com/currentconditions/v1/%s?apikey=%s'
    r_location = requests.get(URL_LOCATION_KEY % (API_KEY, lat, lng))
    data = r_location.json() #json.loads(r_location.text)
    location_key = data['Key']

    if location_key is not None and location_key != '':
        r_weather = requests.get(URL_CURRENT_WEATHER % (location_key, API_KEY))
        w_data = r_weather.json() #json.loads(r_weather.text)

        temprature = float(w_data[0]['Temperature']['Metric']['Value'])
        weather_description = str(w_data[0]['WeatherText']).lower()
        tag_weathers = [weather_description]
        if 'sun' in weather_description:
            tags = 'sunny, shiny, 맑은'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        elif 'cloud' in weather_description:
            tags = 'cloudy, bleak, 구름, 흐린'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        elif 'rain' in weather_description:
            tags = 'rainy, 비, 비오는'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        if 'warm' in weather_description:
            tags = 'warm, 따뜻한'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        if 'win' in weather_description:
            tags = 'windy, 바람부는'
            tag_weathers.extend([x.strip() for x in tags.split(',')])

        if temprature < 20:
            tags = 'cold, 감기, 추위, 한랭, snow, 눈, cool, low temperature, wintry, ice, icy, 얼음, 아이스, 차가움, chilly, 냉담한, 냉랭한, 오싹한, winter, 겨울'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        elif temprature >= 20 and temprature <= 30:
            tags = 'warm, 따뜻한'
            tag_weathers.extend([x.strip() for x in tags.split(',')])
        else:
            tags = 'hot, 더위'
            tag_weathers.extend([x.strip() for x in tags.split(',')])

        return tag_weathers, location_key

    return [], location_key