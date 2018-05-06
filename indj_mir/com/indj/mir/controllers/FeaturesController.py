from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import HandleAudioFile
import sys
from pyAudioAnalysis import audioTrainTest as aT


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def extract_all_features(request):
    try:
        print('Start handling ....')
        HandleAudioFile.extract_all_files_mp3()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def extract_source_uid(request):
    try:
        print('--- Start handling ...')
        print('sourceUID: ', request.data['sourceUID'])
        HandleAudioFile.extract_song_uid(request.data['sourceUID'])
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def training_regression(request):
    try:
        print('--- Start handling ...')
        aT.featureAndTrainRegression("/home/dinhkhoi1/data/songs/train/", 1, 1, aT.shortTermWindow, aT.shortTermStep, "svm",
                                     "/home/dinhkhoi1/data/songs/train/svm_model", False)
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_all_name_song(request):
    try:
        print('Start handling ....')
        HandleAudioFile.get_all_name_file_mp3()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)

