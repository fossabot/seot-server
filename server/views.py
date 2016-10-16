from django.http import HttpResponse
from django.viwes.decorators.csrf import csrf_exempt

import django_filters

from rest_framework import filters, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Agent, App, User
from .serializer import AcceptSerializer, HeartbeatSerializer


class HeartbeatResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

    def heartbeat_response(request):
        return JSONResponse(serializer.errors, status=400)

    def accept_response(request):
        return JSONResponse(serializer.errors, status=400)

# Create your views here.
