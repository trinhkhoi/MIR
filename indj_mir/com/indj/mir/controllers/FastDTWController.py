from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from indj_mir.com.indj.mir.services import FastDTW
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import HandleAudioFile
import sys


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def execute_all_songs(request):
    try:
        print('Start handling ....')
        HandleAudioFile.handle_all_files_mp3()
        FastDTW.calculate_all_songs()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def execute_source_uid(request):
    try:
        print('--- Start handling ...')
        print('sourceUID: ', request.data['sourceUID'])
        HandleAudioFile.handle_song_uid(request.data['sourceUID'])
        HandleAudioFile.convert_mp3_wav(request.data['sourceUID'] + '.mp3')
        FastDTW.calculate_mfcc(request.data['sourceUID'] + '.mp3')
        HandleAudioFile.remove_mp3_wav_file(request.data['sourceUID'] + '.mp3')
        FastDTW.calculate_by_source_uid(request.data['sourceUID'])
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)
