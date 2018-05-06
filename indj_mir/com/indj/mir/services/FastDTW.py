import librosa
import os
from collections import OrderedDict
import sys
from fastdtw import fastdtw
from django.conf import settings
import h5py
from indj_mir.com.indj.mir.respository import SimilarityRepository


def raise_exception(func_name, ex):
    raise Exception('Function {0}: {1} - Line: {2}'.format(func_name, ex, sys.exc_info()[-1].tb_lineno))


def get_song_uids():
    try:
        # get all hdf5 files in the path
        hdf5_files = os.listdir(settings.OUTPUT_PATH_HDF5)
        song_uids = list(map(lambda x: str(x).replace('.hdf5', ''), hdf5_files))
        return song_uids
    except Exception as ex:
        raise_exception(get_song_uids.__name__, ex)


def calculate_mfcc(song_name):
    try:
        print('--- Start calculating mfcc')
        # load time series of each wav file
        y,s = librosa.load('%s%s%s' % (settings.OUTPUT_PATH_WAV, '/', str(song_name).replace('.mp3', '.wav')))
        print('Source load: ', y)
        # MFCC extraction from source
        mfcc = librosa.feature.mfcc(y,s)
        print('MFCC load sucuccessfully: ')

        if not os.path.exists(settings.OUTPUT_PATH_HDF5):
            os.makedirs(settings.OUTPUT_PATH_HDF5)
        data_file = h5py.File('%s%s.hdf5' % (settings.OUTPUT_PATH_HDF5,str(song_name).replace('.mp3', '')), 'w')
        data_file.create_dataset('mfcc', data=mfcc)
        data_file.close()
        print('Store HDF5 Sucessfully: ---------------')

    except Exception as ex:
        raise_exception(calculate_mfcc.__name__, ex)


def get_mfcc_hdf5(song_uids):
    try:
        count = len(song_uids)
        data = {}
        print('--- Start get %s hdf5 files' % count)
        for song_name in song_uids:
            try:
                filename = '%s%s.hdf5' % (settings.OUTPUT_PATH_HDF5, song_name)
                # replace hdf5 format with numpy
                with h5py.File(filename, 'r') as hf:
                    mfcc = hf['mfcc'][:]
                    # Get the data
                    data[song_name] = mfcc
            except Exception:
                raise Exception

        # Sort a dictionary by key name
        data = OrderedDict(sorted(data.items(), key=lambda t: t[0]))
        print('--- End get hdf5 files')
        return data
    except Exception as ex:
        raise_exception(get_mfcc_hdf5.__name__, ex)


def calculate_distance(data, source, target):
    try:
        # calculate distance of source and target for each task
        s = data[source].T
        t = data[target].T
        distance, _ = fastdtw(s, t, radius=100)
        if distance >= 9999999:
            print(' ======== source: ', source, 'target: ', target, 'distance: ', distance)

        similarity = distance / 10000000
        return similarity
    except Exception as ex:
        raise_exception(calculate_distance.__name__, ex)


def build_task_all_song(song_uids):
    print('--- Start creating tasks')
    # set up tasks to compare
    tasks = []
    for i in range(1, len(song_uids)):
        for j in range(0, i):
            source = song_uids[i]
            target = song_uids[j]
            tasks.extend([(source, target)])
    print('--- End of building tasks')
    return tasks


def insert_data_database(data):
    for source_uid, similar_uid, similarity in data:
        SimilarityRepository.insert_data(source_uid, similar_uid, similarity)


def calculate_all_songs():
    try:
        song_uids = get_song_uids()
        if len(song_uids) > 1:
            data = get_mfcc_hdf5(song_uids)
            print('--- Start calculate')
            total_record = 0
            similarities = []
            for source, target in build_task_all_song(song_uids):
                similarity = calculate_distance(data, source, target)
                similarities.extend([(source, target, similarity)])
                if len(similarities) == 10:
                    insert_data_database(similarities)
                    similarities = []
                    total_record += 10
                    print('--- Insert %s record successfully' % total_record)

            insert_data_database(similarities)
            print('--- Insert %s record successfully' % total_record+len(similarities))
        else:
            print('**** Stoping .... Because there is one song file found')
        print('--- End calculate')
    except Exception as ex:
        raise_exception(calculate_all_songs.__name__, ex)


def calculate_by_source_uid(source_uid):
    song_uids = get_song_uids()
    if len(song_uids) > 1:
        data = get_mfcc_hdf5(song_uids)

        # set up tasks to compare
        total_record = 0
        similarities = []
        for i in range(0, len(song_uids)):
            if source_uid != song_uids[i][0]:
                similarity = calculate_distance(data, source_uid, song_uids[i][0])
                similarities.extend([(source_uid, song_uids[i][0], similarity)])
                if len(similarities) == 10:
                    insert_data_database(similarities)
                    similarities = []
                    total_record += 10
                    print('--- Insert %s record successfully' % total_record)
        insert_data_database(similarities)
        print('--- Insert %s record successfully' % total_record + len(similarities))
    else:
        print('**** Stoping .... Because there is one song file found')

if __name__ == "__main__":
    calculate_all_songs()
