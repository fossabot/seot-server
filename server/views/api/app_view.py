import enum
import json
import os
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from server.models.agent import Agent
from server.models.app import App
from server.models.app_status import AppStatus
from server.models.job import Job
from server.models.node import Node
from server.models.nodetype import NodeType
from server.models.uuid import UUID4
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/files'


class AppView:
    @staticmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def launch(request, app_id):
        try:
            app = App.objects.get(id=app_id)
            if make_jobs(app):
                app_request_base(
                        request, app_id, RequestStatus.accept.value)
        except ObjectDoesNotExist:
            print("app DoesNotExist")
        finally:
            return HttpResponseRedirect(reverse('toppage'))

    @staticmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def stop(request, app_id):
        app_request_base(request, app_id, RequestStatus.stop.value)
        return HttpResponseRedirect(reverse('toppage'))


def app_request_base(request, app_id, request_status):
    # uuidがuuid4に準拠しているかどうか
    if UUID4.validate(app_id) is None:
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
            str(app.id) + "_" + str(index),
            next_nodes,
            already_asigned_agents)
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
                print("couldn't create job")
                return None
    create_zmq_pare(app)
    return jobs


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


# nodeが始端ノードであるか判定
def is_source(node):
    num = node.before_nodes.count()
    if num == 0:
        return True
    return False


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
            zmq_source.next_nodes.add(n)

            node.job.nodes.add(zmq_sink)
            n.job.nodes.add(zmq_source)

            app.nodes.add(zmq_sink)
            app.nodes.add(zmq_source)

            addr = str(n.job.allocated_agent.ip_addr)
            port = str(n.job.allocated_agent.dpp_listen_port)
            target_ip_addr = {}
            target_ip_addr['url'] = 'tcp://'\
                                    + addr\
                                    + ':'\
                                    + port
            zmq_sink.args = json.dumps(target_ip_addr)
            zmq_sink.save()


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
