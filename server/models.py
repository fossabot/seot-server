from decimal import Decimal
from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)


class App(models.Model):
    app_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)


class NodeType(models.Model):
    name = models.CharField(max_length=128)


class Agent(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    agent_id = models.CharField(max_length=128, default='0')
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    default=Decimal('0.0'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   default=Decimal('0.0'))
    busy = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    dpp_listen_port = models.IntegerField(default=51423)
#     nodes = models.ManyToManyField(NodeType, related_name="agents")
    available_node_types = models.ManyToManyField(NodeType,
                                                  related_name="agents")


class Job(models.Model):
    name = models.CharField(max_length=128, default='')
    job_id = models.CharField(max_length=256, default='')
    application_id = models.CharField(max_length=256, default='')
    # application = models.ForeignKey(App, related_name='jobs')


class Node(models.Model):
    name = models.CharField(max_length=128, default='')
    node_type = models.ForeignKey(NodeType, related_name="nodes")
    args = models.CharField(max_length=256, default='')
    to = models.CharField(max_length=256, default='')
    job = models.ForeignKey(Job, related_name="nodes")