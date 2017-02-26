import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from .nodetype import NodeType


class Agent(models.Model):
    # 初期listenポート番号
    DEFAULT_LISTEN_PORT = 51423
    # 現在zmq_source_nodeによって使用されているポート番号のリスト
    used_ports = []

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user = models.ForeignKey(
            User,
            related_name="agents",
            blank=True,
            null=True)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)

    # 次にzmq_source_nodeが生成されたとき、待ち受けポート番号として利用される
    # ポート番号
    dpp_listen_port = models.IntegerField(default=DEFAULT_LISTEN_PORT)
    available_node_types = models.ManyToManyField(
            'NodeType',
            related_name="agents",)
    ip_addr = models.CharField(max_length=64, default='127.0.0.1')
    hostname = models.CharField(max_length=128, default='agent')
    active = models.BooleanField(default=True)

    # すでに持っているNodeTypeを破棄し、新しいNodeTypeに変更する
    def update_nodetypes(self, new_nodetype_names):
        self.available_node_types.clear()
        for name in new_nodetype_names:
            nt, created = NodeType.objects.get_or_create(
                name=str(name))
            self.available_node_types.add(nt)

    def update_latest_heartbeat_at(self, time):
        self.latest_heartbeat_at = time

    def open_used_port(self, port):
        if port in self.used_ports:
            self.used_ports.remove(port)

    def update_listen_port(self):
        self.used_ports.append(self.dpp_listen_port)
        new_listen_port = DEFAULT_LISTEN_PORT
        while new_listen_port in self.used_ports:
            new_listen_port += 1
        self.dpp_listen_port = new_listen_port
        self.save()

    def __str__(self):
        return '%s' % (self.id)
