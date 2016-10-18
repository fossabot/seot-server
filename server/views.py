from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import filters, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Agent
from .serializer import AgentSerializer, HeartbeatSerializer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# @csrf_exempt
@api_view(['POST'])
def heartbeat_response(request):
    data = JSONParser().parse(request)
    agent, created = Agent.objects.get_or_create(user_id=data['user_id'])
    if created:
        serializer = AgentSerializer(agent, data=data)
    else:
        serializer = AgentSerializer(agent, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        response = {
                "app_ofer": True,
                "app_id": 1,
                "agent_ip": "127.0.0.2",
                "timestamp": datetime.now(),
        }
        return JSONResponse(response, status=201)
    return JSONResponse(serializer.errors, status=400)
