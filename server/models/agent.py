import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from .nodetype import NodeType


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user = models.ForeignKey(User,
                             related_name="agents",
                             blank=True,
                             null=True)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    created_at = models.DateTimeField(default=timezone.now)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    dpp_listen_port = models.IntegerField(default=51423)
    available_node_types = models.ManyToManyField(NodeType,
                                                  related_name="agents",)
    ip_addr = models.CharField(max_length=64, default='127.0.0.1')
    hostname = models.CharField(max_length=128, default='agent')

    # すでに持っているNodeTypeを破棄し、新しいNodeTypeに変更する
    def update_nodetypes(self, new_nodetype_names):
        self.available_node_types.clear()
        for name in new_nodetype_names:
            nt, created = NodeType.objects.get_or_create(
                name=str(name))
            self.available_node_types.add(nt)

    def update_latest_heartbeat_at(self, time):
        self.latest_heartbeat_at = time

    def __str__(self):
        return '%s' % (self.id)
