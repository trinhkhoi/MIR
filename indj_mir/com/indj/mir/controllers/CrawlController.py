from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import CrawlTorrentFileService as CrawlService
from indj_mir.com.indj.mir.services import ChannelService
import sys


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def crawl_channel_image(request):
    try:
        print('Start handling ....')
        ChannelService.crawl_channel(request.data['start_row'])
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def crawl_song_torrent(request):
    try:
        print('Start handling ....')
        CrawlService.add_torrent_link()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)