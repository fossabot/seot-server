from __future__ import absolute_import, unicode_literals
from datetime import datetime
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import utc
import yaml
from .models import Agent, App, AppDefineFile, Node, NodeType, User
from .serializer import AppSerializer, NodeSerializer


@shared_task
def check_timeout():
    print('timeout')
    today = datetime.utcnow().replace(tzinfo=utc)
    delay = timedelta(seconds=10)
    for agent in Agent.objects.filter(latest_heartbeat_at__lte=today - delay):
        print(agent)
        agent.delete()


@shared_task
def find_files_on_hold():
    print('find app_define_files on hold')
    files_on_hold = []
    for app_define_file in AppDefineFile.objects.filter(hold=True):
        print(app_define_file)
        files_on_hold.append(app_define_file)
    return files_on_hold


@shared_task
def load_and_schedule_app(app_define_file):
    # 例外処理すること
    # yamlロード時にスキーマをチェックするバリデーション処理を加えること
    f = app_define_file.yaml_file
    f.open(mode='rb')
    app_data = yaml.load(f)
    print(app_data)
    f.close()

    user = User.objects.get(name=app_define_file.user)
    app = App.objects.create(name=app_define_file.name, user=user)
    app_serializer = AppSerializer(app)
    if app_serializer.is_valid():
        app_serializer.save()
        # yamlロード時にschemeチェックしとけば下のif節不要
        if isinstance(app_data, list):
            nodes = []
            for node_data in app_data:
                node = Node.objects.create(**node_data)
                node_serializer = NodeSerializer(node)
                if node_serializer.is_valid():
                    node_serializer.save()
                    nodes.append(node)

    # nodeのtoを整理する処理を行うこと

    # ループのネスト再考すること
    sensehat_source = NodeType.objects.filter(name='SenseHatSource')
    already_used_agent = []
    while len(nodes) != 0:
        for node in nodes:
            if node.node_type == sensehat_source:
                for agent in Agent.objects.filter(
                        available_node_types__in=sensehat_source):
                    if agent not in already_used_agent:
                        # jobオブジェクト作成
                        nodes.remove(node)
                        already_used_agent.append(agent)

        for node in nodes:
