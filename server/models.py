import uuid
from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.utils import timezone
from django.utils.html import format_html


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True, unique=True)
    auth_user = models.OneToOneField(AuthUser,
                                     on_delete=models.CASCADE,
                                     blank=True,
                                     null=True,)

    def __str__(self):
        return '%s' % (self.name)


class App(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User, related_name="apps", blank=True, null=True)
    define_file = models.FileField(upload_to='uploads/app_define_files/',
                                   blank=True, null=True)
    upload_time = models.DateTimeField(default=timezone.now)
    hold = models.BooleanField(default=True)

    def file_link(self):
        if self.yaml_file:
            return format_html(
                    '<a href="{}">download file<>',
                    self.define_file.url)
        else:
            return "No attachment"

    def __str__(self):
        return '%s' % (self.name)


class NodeType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)

    def __str__(self):
        return '%s' % (self.name)


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user = models.ForeignKey(User,
                             related_name="agents",
                             blank=True,
                             null=True)
#     user = models.ForeignKey(User,
#                              models.SET_NULL,
#                              related_name='agents',
#                              blank=True,
#                              null=True)
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    busy = models.BooleanField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    dpp_listen_port = models.IntegerField(default=51423)
    available_node_types = models.ManyToManyField(NodeType,
                                                  related_name="agents",)
    ip_addr = models.CharField(max_length=64, default='127.0.0.1')

    def __str__(self):
        return '%s' % (self.id)


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    application = models.ForeignKey(App,
                                    models.SET_NULL,
                                    related_name='jobs',
                                    blank=True,
                                    null=True)
    allocated_agent = models.ForeignKey(Agent,
                                        models.SET_NULL,
                                        related_name='allocated_jobs',
                                        blank=True,
                                        null=True)
    runnning = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % (self.id)


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_type = models.ForeignKey(NodeType,
                                  related_name="nodes",
                                  null=True,
                                  blank=True)
    args = models.CharField(max_length=256, default='')
    next_nodes = models.ManyToManyField('self',
                                        related_name="before_nodes",
                                        blank=True,)
    name = models.CharField(max_length=128, default='')
    job = models.ForeignKey(Job,
                            models.SET_NULL,
                            related_name="nodes",
                            blank=True,
                            null=True)
    application = models.ForeignKey(App,
                                    models.SET_NULL,
                                    related_name="nodes",
                                    blank=True,
                                    null=True)

    def type_name(self):
        return self.node_type.name

    def to(self):
        to_nodes = []
        for n in self.next_nodes.all():
            to_nodes.append(n.name)
        return to_nodes

    def __str__(self):
        return '%s' % (self.name)
