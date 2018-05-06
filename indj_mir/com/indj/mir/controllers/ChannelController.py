from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import SongService
from indj_mir.com.indj.mir.services import ChannelService
from indj_mir.com.indj.mir.services import UserService
from indj_mir.com.indj.mir.services import RecommendationService as RS
import sys
import time


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def recommend(request):
    try:
        start = time.time()
        print('Start handling .... ', request.data['user_uid'])
        ChannelService.first_recommend(request.data['user_uid'])
        stop = time.time()
        print('Total time: ', stop - start)
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def runbatch_recommend(request):
    try:
        print('Start handling ....')
        RS.recommend()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def runbatch_aggregate_channel(request):
    try:
        start = time.time()
        print('Start handling ....')
        ChannelService.aggregate_channel_information()
        stop = time.time()
        print('Total time: ', stop - start)
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def calculate_condition_stuation(request):
    try:
        start = time.time()
        print('Start handling .... ', request.data['user_uid'])
        ChannelService.first_recommend(request.data['user_uid'])
        stop = time.time()
        print('Total time: ', stop - start)
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)