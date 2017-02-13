import enum
import json
import os
import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

import yaml
from .forms import AppForm
from .models.agent import Agent
from .models.app import App
from .models.job import Job
from .models.node import Node
from .models.nodetype import NodeType
from .models.status import AppStatus, JobStatus
from .serializer import NodeSerializer
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/files'


class RequestStatus(enum.Enum):
    accept = 1
    stop = 2

    @classmethod
    def choice(cls):
        return [(m.value, m.name) for m in cls]


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def nodetypes_create_and_add(agent, nodetypes_data):
    agent.available_node_types.clear()
    for nodetype_data in nodetypes_data:
        node_type, created = NodeType.objects.get_or_create(
                name=str(nodetype_data))
        agent.available_node_types.add(node_type)
        node_type.save()


@csrf_exempt
@api_view(['POST'])
@parser_classes((JSONParser, ))
def heartbeat_response(request):
    data = JSONParser().parse(request)

    try:
        user = User.objects.get(username=data['user_name'])
        agent, created = Agent.objects.get_or_create(
                id=data['agent_id'],
                user_id=user.id,
                latitude=data['latitude'],
                longitude=data['longitude'],
                ip_addr=data['facts']['ip'],
                hostname=data['facts']['hostname'])
        nodetypes_create_and_add(agent, data['nodes'])
        job = Job.objects.get(allocated_agent_id=agent.id)
        if job.application.status == AppStatus.launching.value and\
                job.status == JobStatus.idle.value:
            # AppがlaunchingでJobがidleのとき
            response = {
                "run": job.id,
                "kill": None,
            }
            job.status = JobStatus.accept_pending.value
            job.save()
            return JSONResponse(response, status=200)
        elif job.application.status == AppStatus.stopping.value and\
                job.status == JobStatus.running.value:
            # AppがstoppingでJobがrunnningのとき
            response = {
                "run": None,
                "kill": job.id,
            }
            job.status = JobStatus.stop_pending.value
            job.save()
            return JSONResponse(response, status=200)
        else:
            response = {
                "run": None,
                "kill": None,
            }
            return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        # ジョブがない場合のレスポンス
        response = {
            "run": None,
            "kill": None,
        }
        return JSONResponse(response, status=200)
    except User.DoesNotExist:
        # ユーザが存在しない場合
        return JSONResponse({}, status=400)


def job_request_base(request, job_id, request_status):

    # uuidがuuid4に準拠しているかどうか
    if _validate_uuid4(job_id) is None:
        return JSONResponse({}, status=400)

    try:
        job = Job.objects.get(id=job_id)
        running_nodes = Node.objects.filter(
            job_id=job.id,
            job__allocated_agent_id=job.allocated_agent_id
        )
        for n in running_nodes:
            if request_status == RequestStatus.accept.value:
                n.running = True
            elif request_status == RequestStatus.stop.value:
                n.running = False
            n.save()

        nodes = []
        for n in job.nodes.all():
            node = {
                "name": n.name,
                "type": n.type_name(),
                "args": n.args,
                "to": n.to()
            }
            nodes.append(node)

        # acceptリクエストが来て、Jobステータスがaccept_pendingのとき
        # Jobステータスをrunnningに
        if request_status == RequestStatus.accept.value and\
                job.status == JobStatus.accept_pending.value:
            job.status = JobStatus.running.value
            job.save()
            # appの全jobがrunnningのとき、AppStatusをrunnningに
            if not job.application.jobs.exclude(
                    status=JobStatus.running.value).exists():
                job.application.status = AppStatus.running.value
                job.application.save()
        # stopリクエストが来て、jobステータスがstop_pendingのとき
        # jobステータスをidleに
        elif request_status == RequestStatus.stop.value and\
                job.status == JobStatus.stop_pending.value:
            job.status = JobStatus.idle.value
            job.save()
            # appの全jobがidleのとき、AppStatusをidleに
            if not job.application.jobs.exclude(
                    status=JobStatus.idle.value).exists():
                job.application.status = AppStatus.idle.value
                job.application.save()
                delete_jobs(job.application)

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
                "to": n.to()
            }
            print(n.args)
            if n.args:
                node["args"] = json.loads(n.args)
            nodes.append(node)

        response = {
            "job_id": str(job.id),
            "application_id": str(job.application_id),
            "nodes": nodes
        }
        print(response)
        return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        return JSONResponse({}, status=400)


@csrf_exempt
@parser_classes((JSONParser, ))
def job_accept_request(request, job_id):
    return job_request_base(request, job_id, RequestStatus.accept.value)


@csrf_exempt
@parser_classes((JSONParser, ))
def job_stop_request(request, job_id):
    return job_request_base(request, job_id, RequestStatus.stop.value)


def _validate_uuid4(uuid):
    return re.match(
            "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}\
-[89ab][0-9a-f]{3}-[0-9a-f]{12}", uuid)


@login_required
def ctrl_apps(request):
    app_list = []
    for app in App.objects.filter(user=request.user):
        app_list.append(app)
    return render(request, 'server/ctrl_apps.html', {'app_list': app_list})


@login_required
def toppage(request):
    return render(request, 'server/top.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = AppForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save()
            app.user = request.user
            app.save()
            app_to_nodes(app)
            return HttpResponseRedirect('/complete/')
    else:
        form = AppForm(initial={'user': request.user.username})
    return render(request, 'server/form.html', {'form': form})


# appオブジェクトを受取りnodeオブジェクト群を生成
def app_to_nodes(app):
    define_file = app.define_file
    define_file.open(mode='rb')
    nodes_data = yaml.load(define_file)
    define_file.close()
    return nodes_data_to_obj(app, nodes_data)


# nodeオブジェクトデータのリストからnodeオブジェクト生成
def nodes_data_to_obj(app, nodes_data):
    exist_nodes = []
    while True:
        node_gen = [n for n in nodes_data if 'to' not in n or
                    list_contains_list([n.name for n in exist_nodes], n['to'])]
        for node_data in node_gen:
            node = serialize_node(node_data)
            if node is not None:
                app.nodes.add(node)
                exist_nodes.append(node)
                if 'to' in node_data:
                    [node.next_nodes.add(n)
                     for n in exist_nodes if n.name in node_data['to']]
            nodes_data.remove(node_data)
        if len(nodes_data) == 0:
            return exist_nodes
        elif len(exist_nodes) == 0:
            return None


# python辞書型データからserializerを通してnodeオブジェクト保存
def serialize_node(node_data):
    # シリアライザに突っ込む前に、
    # argsがあればjson文字列に変換してargs_strフィールドに格納
    # もっとスマートな方法探す
    if 'args' in node_data:
        node_data['args_str'] = json.dumps(node_data['args'])
    serializer = NodeSerializer(data=node_data)
    if serializer.is_valid():
        return serializer.save()
    else:
        print(serializer.errors)
        return None


# parent_list内にchild_listの要素がすべて含まれているか
def list_contains_list(parent_list, child_list):
    return [n for n in parent_list if n in child_list] == child_list


# nodeが始端ノードであるか判定
def is_source(node):
    num = node.before_nodes.count()
    if num == 0:
        return True
    return False


# nodeをjob, appにadd
# addした後next_nodesを更新
def add_node(node, job, next_nodes):
    job.nodes.add(node)
    for next_node in node.next_nodes.all():
        # next_nodes内に重複要素が出ないよう確認、
        # また、next_nodesが既にjobに割り当てられていないか確認してからappend
        if next_node.name not in [n.name for n in next_nodes] and\
                next_node.job is None:
            next_nodes.append(next_node)
    if node in next_nodes:
        next_nodes.remove(node)


# ジョブの中に与えられたノードタイプのノードがあるか？
def type_of_node_in_job(node_type_name, job):
    if job.nodes is not None and node_type_name is not None:
        return job.nodes.filter(
                node_type__name=node_type_name).exists()
    return False


# ノードタイプがセンサ系か否か
# センサ系ならノード名文字列を、そうでなければNullを返す
def type_of_sensor(node):
    if node.node_type is not None:
        if node.node_type.name in [
                "StubSenseHatSource",
                "SenseHatSource",
                "PiCameraSource"]:
            return node.node_type.name
    return None


# next_nodesのうちagentで動かせるノードを1つ返す
# また、jobへ既にセンサノードが割り当てられている時は、
# 同じタイプのセンサノードは割り当てない
# すでにjobが存在していてわりあてるagentも決まっているとき、
# このメソッドで次に割り当てるnodeを参照する
def find_next_node(next_nodes, job):
    executable_nodes = [
            node for node in next_nodes
            if job.allocated_agent.available_node_types.filter(
                name=node.node_type.name)
            and not type_of_node_in_job(type_of_sensor(node), job)
            ]
    if executable_nodes:
        node = executable_nodes[0]
        next_nodes.remove(node)
        return node
    return None


# job内の末端ノードで、かつ、別job内に位置するnext_nodesを持つノードを
# 選び出し、そのノードとnext_nodesとの間に ZMQSink / ZMQSourceのペアを挿入
def create_zmq_pare(app):
    zmq_sink_type = NodeType. objects.get(name="ZMQSink")
    zmq_source_type = NodeType.objects.get(name="ZMQSource")

    for node in app.nodes.all():
        for n in node.next_nodes.exclude(job=node.job):
            zmq_sink = Node.objects.create(
                node_type=zmq_sink_type,
                name=node.name + "_to_" + n.name + "_sink")
            zmq_source = Node.objects.create(
                node_type=zmq_source_type,
                name=node.name + "_to_" + n.name + "_source")
            node.next_nodes.remove(n)
            node.next_nodes.add(zmq_sink)
            zmq_sink.next_nodes.add(zmq_source)
            zmq_source.next_nodes.add(n)

            node.job.nodes.add(zmq_sink)
            n.job.nodes.add(zmq_source)

            app.nodes.add(zmq_sink)
            app.nodes.add(zmq_source)


# 新しいjobをnameを指定して生成
# job未割り当てなnodeから適当に一つ選択
# 選択したnodeを動かせるagentを選択
def create_new_job(name, next_nodes, asigned_agents):
    job = Job.objects.create(name=name)
    node = next_nodes.pop()
    agent_list = [a for a in Agent.objects.filter(
        available_node_types__name__contains=node.node_type.name)
        if a not in asigned_agents]
    if agent_list:
        agent = agent_list.pop()
        agent.allocated_jobs.add(job)
        return job, node, agent
    else:
        return None, None, None


# appからjob群を生成
def make_jobs(app):
    index = 0
    jobs = []
    already_asigned_agents = []
    nodes = app.nodes.all()
    nodes_list = []
    for n in nodes:
        nodes_list.append(n)
    if not nodes_list:
        return None
    next_nodes = [n for n in nodes_list if is_source(n)]
    job, node, agent = create_new_job(
            str(app.id) + "_" + str(index), next_nodes, already_asigned_agents)
    index += 1
    while True:
        add_node(node, job, next_nodes)
        nodes_list.remove(node)
        if len(nodes_list) == 0:
            app.jobs.add(job)
            job.save()
            jobs.append(job)
            break
        node = find_next_node(next_nodes, job)
        if node is not None:
            pass
        else:
            app.jobs.add(job)
            job.save()
            jobs.append(job)
            already_asigned_agents.append(agent)
            job, node, agent = create_new_job(
                str(app.id) + "_" + str(index),
                next_nodes, already_asigned_agents)
            index += 1
            if job is None:
                print(jobs)
                print("couldn't create job")
                return None
    create_zmq_pare(app)
    return jobs


def complete(request):
    return render(request, 'server/complete.html')


def app_request_base(request, app_id, request_status):

    # uuidがuuid4に準拠しているかどうか
    if _validate_uuid4(app_id) is None:
        return JSONResponse({}, status=400)

    try:
        app = App.objects.get(id=app_id)
        if request_status == RequestStatus.accept.value:
            app.status = AppStatus.launching.value
        elif request_status == RequestStatus.stop.value:
            app.status = AppStatus.stopping.value
        app.save()
        response = {
            "app_id": str(app.id),
            "app_status": str(app.status)
        }
        return JSONResponse(response, status=200)
    except Job.DoesNotExist:
        return JSONResponse({}, status=400)


@csrf_exempt
@parser_classes((JSONParser, ))
def app_launch_request(request, app_id):
    try:
        app = App.objects.get(id=app_id)
        if make_jobs(app):
            app_request_base(request, app_id, RequestStatus.accept.value)
    except ObjectDoesNotExist:
        print("app DoesNotExist")
    finally:
        return HttpResponseRedirect(reverse('ctrl_apps'))


@csrf_exempt
@parser_classes((JSONParser, ))
def app_stop_request(request, app_id):
    app_request_base(request, app_id, RequestStatus.stop.value)
    return HttpResponseRedirect(reverse('ctrl_apps'))


def delete_jobs(app):
    for j in app.jobs.all():
        j.delete()
