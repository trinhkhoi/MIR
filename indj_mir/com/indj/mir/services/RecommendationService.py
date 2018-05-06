from __future__ import print_function
import argparse
import logging
import time
import numpy
import pandas
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
from implicit.approximate_als import (AnnoyAlternatingLeastSquares, FaissAlternatingLeastSquares,
                                      NMSLibAlternatingLeastSquares)
from implicit.nearest_neighbours import (BM25Recommender, CosineRecommender,
                                         TFIDFRecommender, bm25_weight)
from indj_mir.com.indj.mir.respository import UserRepository as URepository
from indj_mir.com.indj.mir.respository import SongsRepository as SRepository
from indj_mir.com.indj.mir.respository import RecommendConditionRespository as RCRepository
from indj_mir.com.indj.mir.services import ChannelService as CService
import pandas as pd
from random import randint
import ast


# maps command line model argument to class name
MODELS = {"als":  AlternatingLeastSquares,
          "nmslib_als": NMSLibAlternatingLeastSquares,
          "annoy_als": AnnoyAlternatingLeastSquares,
          "faiss_als": FaissAlternatingLeastSquares,
          "tfidf": TFIDFRecommender,
          "cosine": CosineRecommender,
          "bm25": BM25Recommender}


def get_model(model_name):
    model_class = MODELS.get(model_name)
    if not model_class:
        raise ValueError("Unknown Model '%s'" % model_name)

    # some default params
    if issubclass(model_class, AlternatingLeastSquares):
        params = {'factors': 64, 'dtype': numpy.float32, 'use_gpu': False}
    elif model_name == "bm25":
        params = {'K1': 100, 'B': 0.5}
    else:
        params = {}

    return model_class(**params)


def read_data(filename):
    """ Reads in the last.fm dataset, and returns a tuple of a pandas dataframe
    and a sparse matrix of artist/user/playcount """
    # read in triples of user/artist/playcount from the input dataset
    # get a model based off the input params
    start = time.time()
    logging.debug("reading data from %s", filename)
    data = pandas.read_table(filename,
                             usecols=[0, 1, 2],
                             names=['user', 'channel', 'plays'], sep=',')

    # map each artist and user to a unique numeric value
    data['user'] = data['user'].astype("category")
    data['channel'] = data['channel'].astype("category")

    print('data[channel].cat.codes: \n', data['user'])
    print('(data[channel].cat.codes.copy(): \n', data['channel'].cat.codes.copy())
    print('data[plays]: \n', data['plays'])

    # create a sparse matrix of all the users/plays
    plays = coo_matrix((data['plays'].astype(numpy.float32),
                       (data['channel'].cat.codes.copy(),
                        data['user'].cat.codes.copy())))

    logging.debug("read data file in %s", time.time() - start)
    return data, plays


def calculate_recommendations(input_filename, output_filename, model_name="als"):
    """ Generates artist recommendations for each user in the dataset """
    # train the model based off input params
    df, plays = read_data(input_filename)

    # create a model from the input data
    model = get_model(model_name)

    # if we're training an ALS based model, weight input for last.fm
    # by bm25
    if issubclass(model.__class__, AlternatingLeastSquares):
        # lets weight these models by bm25weight.
        logging.debug("weighting matrix by bm25_weight")
        plays = bm25_weight(plays, K1=100, B=0.8)

        # also disable building approximate recommend index
        model.approximate_similar_items = False

    # this is actually disturbingly expensive:
    plays = plays.tocsr()

    logging.debug("training model %s", model_name)
    start = time.time()
    model.fit(plays)
    logging.debug("trained model '%s' in %0.2fs", model_name, time.time() - start)

    # generate recommendations for each user and write out to a file
    artists = dict(enumerate(df['channel'].cat.categories))
    start = time.time()
    user_plays = plays.T.tocsr()
    with open(output_filename, "w") as o:
        for userid, username in enumerate(df['user'].cat.categories):
            for artistid, score in model.recommend(userid, user_plays):
                o.write("%s\t%s\t%s\n" % (username, artists[artistid], score))
    logging.debug("generated recommendations in %0.2fs",  time.time() - start)


def get_all_conditions():

    conditions = URepository.get_all_user_conditions()
    file = open('data-mf.dat', 'w')
    file.write('user,channel,plays\n')
    for user, condition_uid, channels, songs, likesongs, likechannels, dislikesongs, dislikechannels, tags, genres, artists in conditions:
        dictChannels = ast.literal_eval(channels)
        for channel_uid in dictChannels:
            file.write('%s,%s,%s\n' % (user, channel_uid, dictChannels[channel_uid]['play']))

    file.close()

    return conditions


def get_song_conditions(conditions):
    dictSongConditions = {}
    for user, condition_uid, channels, songs, likesongs, likechannels, dislikesongs, dislikechannels, tags, genres, artists in conditions:
        lstConditions = set([x.strip() for x in eval(tags)])
        lstConditions |= set([x.strip() for x in eval(genres)])
        lstConditions |= set([x.strip() for x in eval(artists)])

        if len(eval(likesongs)) > 0:
            for attribute in SRepository.get_artists_genres(eval(likesongs)):
                print('attributes: ', attribute)
                lstConditions.add(attribute)
        print('conditions: ', lstConditions)
        dictSongConditions.update({condition_uid : lstConditions})

    print('dict_conditions: ', dictSongConditions)
    return dictSongConditions

def recommend(user_uid='user_uid'):
    conditions = get_all_conditions()
    if len(conditions) <= 100:
        dictSongConditions = get_song_conditions(conditions)
        for condition_uid in dictSongConditions:
            # Recommend for home screen
            CService.recommend_by_screen(dictSongConditions[condition_uid], 'home', condition_uid,
                                         CService.get_all_channels_home(), CService.get_top_channels_home(), 'favorite')

            # Recommend for radio screen
            CService.recommend_by_screen(dictSongConditions[condition_uid], 'radio', condition_uid,
                                         CService.get_all_channels_radio(), CService.get_top_channels_radio(), 'favorite')

            # Recommend for cast screen
            CService.recommend_by_screen(dictSongConditions[condition_uid], 'cast', condition_uid,
                                         CService.get_all_casts(), CService.get_hot_casts(), 'favorite')
    else:
        calculate_recommendations('data-mf.dat', 'recommend.dat')


if __name__ == "__main__":
    recommend()