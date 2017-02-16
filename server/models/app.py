import json
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from server.serializer import NodeSerializer
import yaml
from .app_scheduler import AppScheduler
from .app_status import AppStatus


class App(models.Model, AppScheduler):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User, related_name="apps", blank=True, null=True)
    define_file = models.FileField(upload_to='uploads/app_define_files/',
                                   blank=True, null=True)
    upload_time = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(
        choices=AppStatus.choices(),
        default=AppStatus.idle.value,
        verbose_name='App Status'
    )

    def download_link_tag(self):
        if self.yaml_file:
            return format_html(
                    '<a href="{}">download file<>',
                    self.define_file.url)
        else:
            return "No attachment"

    # 登録されているジョブを全てクリア（削除）する
    def clear_jobs(self):
        self.jobs.all().delete()

    def __str__(self):
        return '%s' % (self.name)

    # ymlファイルロードしてnodeインスタンス群を生成
    def setup_nodes(self):
        define_file = self.define_file
        define_file.open(mode='rb')
        define_yml = yaml.load(define_file)
        define_file.close()
        return self._setup_nodes_from_list(define_yml['nodes'])

    # nodeオブジェクトデータのリストからnodeオブジェクト生成、
    # app自身に紐付ける
    def _setup_nodes_from_list(self, n_list):
        exist_nodes = {}
        for node_data in n_list:
            if 'args' in node_data:
                node_data['args_str'] = json.dumps(node_data['args'])
            serializer = NodeSerializer(data=node_data)
            node = None
            if serializer.is_valid():
                node = serializer.save()
            else:
                print(serializer.errors)
            if node is not None:
                self.nodes.add(node)
                exist_nodes[node_data] = node
        for node_data, node in exist_nodes.items():
            if 'to' in node_data:
                [node.next_nodes.add(n)
                 for n in exist_nodes.values()
                 if n.name in node_data['to']]
        return exist_nodes.values()
