from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return '%s' % (self.name)


class App(models.Model):
    app_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return '%s' % (self.name)


class NodeType(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return '%s' % (self.name)


class Agent(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    agent_id = models.CharField(max_length=128, default='0')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    busy = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    dpp_listen_port = models.IntegerField(default=51423)
    available_node_types = models.ManyToManyField(NodeType,
                                                  related_name="agents",)
    ip_addr = models.CharField(max_length=64, default='127.0.0.1')

    def __str__(self):
        return '%s' % (self.agent_id)


class Job(models.Model):
    name = models.CharField(max_length=128, default='')
    job_id = models.CharField(max_length=256, default='')
    application = models.ForeignKey(App,
                                    models.SET_NULL,
                                    related_name='jobs',
                                    blank=True,
                                    null=True,)

    def __str__(self):
        return '%s' % (self.name)


class Node(models.Model):
    args = models.CharField(max_length=256, default='')
    to = models.CharField(max_length=256, default='')
    name = models.CharField(max_length=128, default='')
    node_type = models.ForeignKey(NodeType,
                                  models.SET_NULL,
                                  related_name="nodes",
                                  blank=True,
                                  null=True,)
    job = models.ForeignKey(Job,
                            models.SET_NULL,
                            related_name="nodes",
                            blank=True,
                            null=True,)
    application = models.ForeignKey(App,
                                    models.SET_NULL,
                                    related_name="nodes",
                                    blank=True,
                                    null=True,)

    def __str__(self):
        return '%s' % (self.name)
