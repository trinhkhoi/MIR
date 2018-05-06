from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import DownloadMp3Youtube as dl
import sys
from django.conf import settings


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def download_all_mp3_songs(request):
    try:
        print('Start handling ....')
        #dl.download_all_mp3s(settings.EXCEL_FILE_DATA_TRAINING)
        dl.download_all_mp3s(settings.EXCEL_SONGS_DATA, 0, 1, 0, request.data['start_row'])
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.strederr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def download_one_mp3(request):
    try:
        print('--- Start handling ...')
        print('Text search: ', request.data['text_search'])
        dl.download_mp3_by_text_search(request.data['text_search'], request.data['file_name'])
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)