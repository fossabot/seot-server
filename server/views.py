import json
import yaml
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
# from django.utils.ddecorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from .forms import AppForm
from .models import Agent, Node, User
from .serializer import AgentSerializer, NodeSerializer
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/files'


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
    # 既存のモデルオブジェクトがあるかDBから探して、
    # 存在していた場合はdataで上書き
    # 存在していなければ作成
    # もっと綺麗な方法をあとで探す
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


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save()
            user = User.objects.get(auth_user=request.user)
            app.user = user
            app.save()
            nodes = make_nodes(app)
            return HttpResponseRedirect('/complete/')
    else:
        form = AppForm(initial={'user': request.user.username})
    return render(request, 'server/form.html', {'form': form})


def make_nodes(app):
    define_file = app.define_file
    define_file.open(mode='rb')
    nodes_data = yaml.load(define_file)
    define_file.close()

    already_exist_nodes = {}
    while len(nodes_data) > 0:
        for node_data in nodes_data:
            if 'to' not in node_data or\
            next_nodes_are_already_exist(already_exist_nodes, node_data['to']):
                if 'args' in node_data:
                    node_data['args_str'] = json.dumps(node_data['args'])
                node_serializer = NodeSerializer(data=node_data)
                if node_serializer.is_valid():
                    node = node_serializer.save()
                    already_exist_nodes[node.name] = node
                    if 'to' in node_data:
                        for next_node_name in node_data['to']:
                            node.next_nodes.add(already_exist_nodes[next_node_name])
                    app.nodes.add(node)
                    nodes_data.remove(node_data)
                else:
                    print(node_serializer.errors)
    return already_exist_nodes


def next_nodes_are_already_exist(exist_nodes, next_nodes):
    for node in next_nodes:
        if node not in exist_nodes:
            return False
    return True

# def make_jobs(app, nodes):
#     next_nodes = []
#     current_target_agent = None
#     job = None
#     index = 0
#     while len(nodes) > 0:
#         for name, node in nodes.items():
#             if 'Source' in name or node in next_nodes:
#                 if current_target_agent is None:
#                     current_target_agent =
#                     Agent.objects.filter(available_node_types__contains=node.node_type)[0]
#                     job = Job.objects.create(
#                             name= app.id + "_" + index,
#
#                             )

def complete(request):
    return render(request, 'server/complete.html')
