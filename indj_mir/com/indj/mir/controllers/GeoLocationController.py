from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from indj_mir.com.indj.mir.services import GeolocationService as ge
import sys

@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def runbatch_cluster_geolocation(request):
    try:
        print('Start handling ....')
        ge.cluster_location()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def import_geolocation_data(request):
    try:
        print('Start handling ....')
        ge.import_geolocation()
        return Response(status=status.HTTP_201_CREATED)
    except Exception as ex:
        sys.stderr(ex)
        return Response(ex.__cause__, status=status.HTTP_400_BAD_REQUEST)