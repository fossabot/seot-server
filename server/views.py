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
    data = JSONParser().parse(request)
    agent, created = Agent.objects.get_or_create(agent_id=data['agent_id'])
    serializer = AgentSerializer(agent, data=data)
    if serializer.is_valid():
        """
        ここにheartbeat受信時の処理を書く
        * request内容読み込み、Agentモデルのインスタンス作成/更新
        * responseを返す
            * Appモデルのインスタンスのうち、agentの割当オファーをしているもの
              を探す
            * heartbeatを送ってきたagentにオファーをだすAppを決める
            * AppのIDを読み取る
        """
        serializer.save()
        # return JSONResponse(serializer.data, status=201)
        response = {
                "job_offer": False,
        }
        return JSONResponse(response, status=200)
    return JSONResponse(serializer.errors, status=400)
