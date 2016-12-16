# from datetime import datetime
#
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

# from rest_framework import filters, viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .models import Agent
from .serializer import AgentSerializer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
@api_view(['POST'])
@parser_classes((JSONParser, ))
def heartbeat_response(request):
    agent_ip_addr = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        agent_ip_addr = x_forwarded_for.split(',')[0]

    data = JSONParser().parse(request)
    data['ip_addr'] = agent_ip_addr
    print(data)
    agent, created = Agent.objects.get_or_create(agent_id=data['agent_id'],
                                                 user_id=data['user_id'],)
    serializer = AgentSerializer(agent, data=data, partial=True)
    if serializer.is_valid():
        """
        ここにheartbeat受信時の処理を書く
        * responseを返す
            * Appモデルのインスタンスのうち、agentの割当オファーをしているもの
              を探す
            * heartbeatを送ってきたagentにオファーをだすAppを決める
            * AppのIDを読み取る
        """
        serializer.save()
        response = {
                "job_offer": False,
        }
        return JSONResponse(response, status=200)
    return JSONResponse(serializer.errors, status=400)
