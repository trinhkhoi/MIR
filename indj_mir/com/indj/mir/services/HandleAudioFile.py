from pydub import AudioSegment
from django.conf import settings
import boto3
from indj_mir.com.indj.mir.services import FastDTW
import h5py
import librosa
import numpy as np
from rp_extract import rp_extract
from rp_extract.audiofile_read import *
import os
import sys
import time


def raise_exception(func_name, ex):
    raise Exception('Function {0}: {1} - Line: {2}'.format(func_name, ex, sys.exc_info()[-1].tb_lineno))

def raise_message_error(func_name, message):
    raise Exception('Function {0}: {1}'.format(func_name, message))


def handle_all_files_mp3():
    # connect to AWS S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(settings.BUCKET_NAME)
    # if blank prefix is given, return everything)
    objs = bucket.objects.filter(
        Prefix=settings.PREFIX)
    print('--- Connect to AWS S3 sucessfully')

    # create folder to store mp3 file if it's not existed
    if not os.path.exists(settings.INPUT_PATH_MP3):
        os.makedirs(settings.INPUT_PATH_MP3)

    for object in objs:
        path, filename = os.path.split(object.key)
        if filename != '':
            # download mp3 file from S3 and store to INPUT_PATH_MP3
            bucket.download_file(object.key, settings.INPUT_PATH_MP3 + filename)
            print('--- Download successfully: ', settings.INPUT_PATH_MP3 + filename)
            convert_mp3_wav(filename)
            FastDTW.calculate_mfcc(filename)
            remove_mp3_wav_file(filename)


def handle_song_uid(song_uid):
    try:
        print('--- Start download ', song_uid)
        KEY = '%s/%s%s' % (settings.PREFIX, song_uid, '.mp3')
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(settings.BUCKET_NAME)

        if not os.path.exists(settings.INPUT_PATH_MP3):
            os.makedirs(settings.INPUT_PATH_MP3)
            print('--- Create input path mp3 successfully')

        bucket.download_file(KEY, '%s%s%s' % (settings.INPUT_PATH_MP3, song_uid, '.mp3'))
        print('--- Download %s successfully' % song_uid)
    except Exception as ex:
        raise_exception(handle_song_uid.__name__, ex)


def convert_mp3_wav(song_name):
    print('--- Start convert mp3 file')
    mp3_song = AudioSegment.from_mp3(settings.INPUT_PATH_MP3 + song_name)
    # create folder to store wav file after converting
    if not os.path.exists(settings.OUTPUT_PATH_WAV):
        os.makedirs(settings.OUTPUT_PATH_WAV)
    # execute convert
    mp3_song.export(settings.OUTPUT_PATH_WAV + '/' + str(song_name).replace('.mp3', '.wav'), format='wav')
    print('--- Convert mp3 to wav successfully: ', song_name)


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)


def remove_mp3_wav_file(song_name):
    mp3_file_path = '%s%s' % (settings.INPUT_PATH_MP3, song_name)
    wav_file_path = '%s%s%s' % (settings.OUTPUT_PATH_WAV, '/', str(song_name).replace('.mp3', '.wav'))

    remove_file(mp3_file_path)
    remove_file(wav_file_path)


def extract_all_files_mp3():
    # connect to AWS S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket(settings.BUCKET_NAME)
    # if blank prefix is given, return everything)
    objs = bucket.objects.filter(
        Prefix=settings.PREFIX)
    print('--- Connect to AWS S3 sucessfully')

    # create folder to store mp3 file if it's not existed
    if not os.path.exists(settings.INPUT_PATH_MP3):
        os.makedirs(settings.INPUT_PATH_MP3)

    file = open('error.txt', 'w')
    for object in objs:
        path, filename = os.path.split(object.key)
        if filename != '':
            # download mp3 file from S3 and store to INPUT_PATH_MP3
            bucket.download_file(object.key, settings.INPUT_PATH_MP3 + filename)
            print('--- Download successfully: ', settings.INPUT_PATH_MP3 + filename)
            convert_mp3_wav(filename)

            # load time series of each wav file
            y, sr = librosa.load('%s%s%s' % (settings.OUTPUT_PATH_WAV, '/', str(filename).replace('.mp3', '.wav')))

            print('====== Start extract all feature ======')
            # Extract all features
            extract_mfcc(y, sr, str(filename).replace('.mp3', ''))
            #mfcc_path = '%s%s_MFCC.hdf5' % ('/data/hdf5s/', str(filename).replace('.mp3', ''))
            #s3.upload_file(mfcc_path, 'indj-features-extraction', mfcc_path)
            extract_spectral_contrast(y, sr, str(filename).replace('.mp3', ''))
            try:
                extract_hamonic(y, str(filename).replace('.mp3', ''))
            except Exception as ex:
                file.write('*** Song_name: %s, Error: %s ' % (filename, ex))

            extract_rhythm_features(y, sr, str(filename).replace('.mp3', ''))

            # Remove mp3 and wav files
            remove_mp3_wav_file(filename)
    file.close()


def get_all_name_file_mp3():
    # connect to AWS S3
    s3 = boto3.resource('s3')

    bucket = s3.Bucket("indj-audiosource-upload")
    # if blank prefix is given, return everything)
    objs = bucket.objects.all()
    print('--- Connect to AWS S3 sucessfully')

    size = sum(1 for _ in objs)
    print('Len bucket: ', size)
    import math
    number_file = math.ceil(size/10000)

    filenames = ['song_name_%s.csv' % i for i in range(number_file)]
    print(filenames)

    count = 0
    file = None
    for i, object in enumerate(objs):
        if i/10000 == count:
            if file is not None:
                file.close()
            file = open(filenames[count], 'w')
            count += 1
        path, filename = os.path.split(object.key)
        file.write('\n%s' % filename)

    if file is not None:
        file.close()


def extract_song_uid(song_name):
    if song_name == '':
        raise_message_error(extract_song_uid.__name__, 'Song name is empty')
    else:
        handle_song_uid(song_name)
        convert_mp3_wav(song_name + '.mp3')

        # load time series of each wav file
        y, sr = librosa.load('%s%s%s' % (settings.OUTPUT_PATH_WAV, '/', song_name + '.wav'))

        print('====== Start extract all feature ======')
        # Extract all features
        extract_mfcc(y, sr, song_name)
        extract_spectral_contrast(y, sr, song_name)
        try:
            extract_hamonic(y, song_name)
        except Exception as ex:
            print('*** Error: ', ex)
        extract_rhythm_features(y, sr, song_name)

        # Remove mp3 and wav files
        remove_mp3_wav_file(song_name + '.mp3')


def upload_file(file_path, file_name, bucket_name):
    # Create an S3 client
    s3 = boto3.client('s3')

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    print('Start upload file ---------')
    s3.upload_file(file_path, bucket_name, file_name)
    print('Upload file successully --------')

    time.sleep(2)
    remove_file(file_path)


def extract_mfcc(y, sr, song_name):
    try:
        print('Start extract MFCC ----- ')
        mfcc = librosa.feature.mfcc(y, sr, n_mfcc=16)
        print('MFCC load sucuccessfully: ')

        # Create output folder if it's not exist
        if not os.path.exists(settings.OUTPUT_PATH_HDF5):
            os.makedirs(settings.OUTPUT_PATH_HDF5)

        file_name = '%s_MFCC.hdf5' % song_name
        file_path = '%s%s' % (settings.OUTPUT_PATH_HDF5, file_name)
        data_file = h5py.File(file_path, 'w')
        data_file.create_dataset('mfcc', data=mfcc)
        data_file.close()
        print('Store HDF5 Local Sucessfully: ---------------')

        # upload MFCC to AWS S3
        upload_file(file_path, file_name, settings.BUCKET_HDF5)

    except Exception as ex:
        raise_exception(extract_mfcc.__name__, ex)


def extract_spectral_contrast(y, sr, song_name):
    try:
        print('Start extract Spectral contrast ----- ')
        S = np.abs(librosa.stft(y))
        spectral_contrast = librosa.feature.spectral_contrast(S=S, sr=sr)
        print('Spectral contrast loaded sucuccessfully: ')

        # Create output folder if it's not exist
        if not os.path.exists(settings.OUTPUT_PATH_HDF5):
            os.makedirs(settings.OUTPUT_PATH_HDF5)

        file_name = '%s_contrast.hdf5' % song_name
        file_path = '%s%s' % (settings.OUTPUT_PATH_HDF5, file_name)
        data_file = h5py.File(file_path, 'w')
        data_file.create_dataset('contrast', data=spectral_contrast)
        data_file.close()
        print('Store Spectral contrast Sucessfully: ---------------')

        # upload MFCC to AWS S3
        upload_file(file_path, file_name, settings.BUCKET_HDF5)

    except Exception as ex:
        raise_exception(extract_spectral_contrast.__name__, ex)


def extract_hamonic(y, song_name):
    try:
        print('Start extract HPSS ----- ')
        D = librosa.stft(y)
        hamonic, percussive = librosa.decompose.hpss(D, mask=True)
        print('HPSS loaded sucuccessfully: ')

        # Create output folder if it's not exist
        if not os.path.exists(settings.OUTPUT_PATH_HDF5):
            os.makedirs(settings.OUTPUT_PATH_HDF5)

        file_name = '%s_hpss.hdf5' % song_name
        file_path = '%s%s' % (settings.OUTPUT_PATH_HDF5, file_name)
        data_file = h5py.File(file_path, 'w')
        data_file.create_dataset('harmonic', data=hamonic)
        data_file.create_dataset('percussive', data=percussive)
        data_file.close()
        print('Store HPSS Sucessfully: ---------------')

        # upload MFCC to AWS S3
        upload_file(file_path, file_name, settings.BUCKET_HDF5)

    except Exception as ex:
        raise_exception(extract_hamonic.__name__, ex)


def extract_rhythm_features(y, sr, song_name):
    print('Start extract rythm ----- ')
    sr, sw, y = audiofile_read('%s%s%s' % (settings.OUTPUT_PATH_WAV, '/', song_name + '.wav'))

    features = rp_extract.rp_extract(y,  # the two-channel wave-data of the audio-file
                          sr,  # the samplerate of the audio-file
                          extract_rp=True,  # <== extract this feature!
                          transform_db=True,  # apply psycho-accoustic transformation
                          transform_phon=True,  # apply psycho-accoustic transformation
                          transform_sone=True,  # apply psycho-accoustic transformation
                          fluctuation_strength_weighting=True,  # apply psycho-accoustic transformation
                          skip_leadin_fadeout=1,  # skip lead-in/fade-out. value = number of segments skipped
                          step_width=1)
    print('Rhythm features loaded sucuccessfully: ')
    print('len feature: ', len(features['rp']))
    print(features)

    # Create output folder if it's not exist
    if not os.path.exists(settings.OUTPUT_PATH_HDF5):
        os.makedirs(settings.OUTPUT_PATH_HDF5)

    file_name = '%s_rhythm.hdf5' % song_name
    file_path = '%s%s' % (settings.OUTPUT_PATH_HDF5, file_name)
    data_file = h5py.File(file_path, 'w')
    data_file.create_dataset('rhythm', data=features['rp'])
    data_file.close()
    print('Store Rhythm features Sucessfully: ---------------')

    # upload MFCC to AWS S3
    upload_file(file_path, file_name, settings.BUCKET_HDF5)


def get_spectral_contrast(song_name):
    try:
        filename = '%s%s_contrast.hdf5' % ('/data/hdf5s/', song_name)
        # replace hdf5 format with numpy
        contrast = []
        with h5py.File(filename, 'r') as hf:
            contrast = hf['contrast'][:]

        print('len spectral contrast: ', len(contrast))
        print('len spectral contrast 0: ', len(contrast[0]))
        return contrast
    except Exception as ex:
        raise_exception(get_spectral_contrast.__name__, ex)


def get_mfcc(song_name):
    try:
        filename = '%s%s_MFCC.hdf5' % ('/data/hdf5s/', song_name)
        mfcc = []
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            mfcc = hf['mfcc'][:]

        print('len mfcc: ', len(mfcc))
        print('len mfcc 0: ', len(mfcc[0]))
        return mfcc
    except Exception as ex:
        raise_exception(get_mfcc.__name__, ex)


def get_harmonic_percussive(song_name):
    try:
        filename = '%s%s_hpss.hdf5' % ('/data/hdf5s/', song_name)
        harmonic = []
        percussive = []
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            harmonic = hf['harmonic'][:]
            percussive = hf['percussive'][:]

        print('len harmonic: ', len(harmonic))
        print('len harmonic 0: ', len(harmonic[0]))
        print('len percussive: ', len(percussive))
        print('len percussive 0: ', len(percussive[0]))
        return harmonic, percussive
    except Exception as ex:
        raise_exception(get_harmonic_percussive.__name__, ex)


def get_rhythm(song_name):
    try:
        filename = '%s%s_rhythm.hdf5' % ('/data/hdf5s/', song_name)
        rhythm = []
        # replace hdf5 format with numpy
        with h5py.File(filename, 'r') as hf:
            rhythm = hf['rhythm'][:]

        print('len rhythm: ', len(rhythm))
        return np.asanyarray(rhythm)
    except Exception as ex:
        raise_exception(get_mfcc.__name__, ex)

if __name__ == "__main__":
    get_spectral_contrast('210013717313010895')
    get_mfcc('210013717313010895')
    get_harmonic_percussive('210013717313010895')