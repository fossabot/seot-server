import uuid
from django.db import models
from .app import App
from .job import Job
from .nodetype import NodeType


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_type = models.ForeignKey(NodeType,
                                  related_name="nodes",
                                  null=True,
                                  blank=True)
    args = models.CharField(max_length=256, default='', blank=True, null=True)
    next_nodes = models.ManyToManyField('self',
                                        symmetrical=False,
                                        related_name="before_nodes",
                                        blank=True)
    name = models.CharField(max_length=128, default='')
    job = models.ForeignKey(Job,
                            models.SET_NULL,
                            related_name="nodes",
                            blank=True,
                            null=True)
    application = models.ForeignKey(
            App,
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
