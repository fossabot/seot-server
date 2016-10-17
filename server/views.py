from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .serializer import AcceptSerializer, HeartbeatSerializer

class HeartbeatViewSet(viewsets.ViewSet):
    def create(self, request):
        pass

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# @csrf_exempt
@api_view(['POST'])
def heartbeat_response(request):
    data = JSONParser().parse(request)
    serializer = HeartbeatSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JSONResponse(serializer.data, status=201)
    return JSONResponse(serializer.errors, status=400)


# @csrf_exempt
@api_view(['POST'])
def accept_response(request):
    serializer = AcceptSerializer()
    return JSONResponse(serializer.errors, status=400)

# Create your views here.
