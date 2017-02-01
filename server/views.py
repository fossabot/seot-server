import json
import os
import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

import yaml

from .forms import AppForm
from .models import Agent, Job, User, App, AppStatus
from .serializer import NodeSerializer
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

    try:
        user = User.objects.get(name=data['user_name'])
        agent, created = Agent.objects.get_or_create(id=data['agent_id'],
                                                     user_id=user.id,)

        job = Job.objects.get(allocated_agent_id=agent.id)
        if job.application.status == AppStatus.running.value:
            # Running状態のジョブが存在
            response = {
                "run": True,
                "kill": False,
                "job_id": job.id
            }
            return JSONResponse(response, status=200)
        else:
            # Running 状態のジョブがない場合のレスポンス
            response = {
                "run": False,
                "kill": False
            }
            return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        # ジョブがない場合のレスポンス
        response = {
            "run": False,
            "kill": False
        }
        return JSONResponse(response, status=200)
    except User.DoesNotExist:
        # ユーザが存在しない場合
        return JSONResponse({}, status=400)


@csrf_exempt
@parser_classes((JSONParser, ))
def job_request(request, job_id):

    # uuidがuuid4に準拠しているかどうか
    if _validate_uuid4(job_id) is None:
        return JSONResponse({}, status=400)

    try:
        job = Job.objects.get(id=job_id)
        nodes = []
        for n in job.nodes.all():
            node = {
                "name": n.name,
                "type": n.type_name(),
                "args": n.args,
                "to": n.to()
            }
            nodes.append(node)

        response = {
            "job_id": str(job.id),
            "application_id": str(job.application_id),
            "nodes": nodes
        }
        return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        return JSONResponse({}, status=400)


@csrf_exempt
@parser_classes((JSONParser, ))
def job_accept_request(request, job_id):
    print("In : JOB_ACCEPT_REQUEST")

    # uuidがuuid4に準拠しているかどうか
    if _validate_uuid4(job_id) is None:
        return JSONResponse({}, status=400)

    try:
        job = Job.objects.get(id=job_id)
        nodes = []
        for n in job.nodes.all():
            node = {
                "name": n.name,
                "type": n.type_name(),
                "args": n.args,
                "to": n.to()
            }
            nodes.append(node)

        response = {
            "job_id": str(job.id),
            "application_id": str(job.application_id),
            "nodes": nodes
        }
        return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        return JSONResponse({}, status=400)


def _validate_uuid4(uuid):
    return re.match(
            "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}\
-[89ab][0-9a-f]{3}-[0-9a-f]{12}", uuid)


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
            make_jobs(app, nodes)
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
            if 'to' not in node_data or next_nodes_are_already_exist(
                    already_exist_nodes, node_data['to']):
                if 'args' in node_data:
                    node_data['args_str'] = json.dumps(node_data['args'])
                node_serializer = NodeSerializer(data=node_data)
                if node_serializer.is_valid():
                    node = node_serializer.save()
                    already_exist_nodes[node.name] = node
                    if 'to' in node_data:
                        for next_node_name in node_data['to']:
                            node.next_nodes.add(
                                    already_exist_nodes[next_node_name])
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


def make_jobs(app, nodes):
    pass


def complete(request):
    return render(request, 'server/complete.html')
