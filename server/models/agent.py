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

    def __str__(self):
        return '%s' % (self.id)
