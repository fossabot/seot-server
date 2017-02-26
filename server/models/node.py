import uuid
from django.db import models


class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_type = models.ForeignKey(
            'NodeType',
            related_name="nodes",
            null=True,
            blank=True)
    args = models.CharField(max_length=256, default='', blank=True, null=True)
    next_nodes = models.ManyToManyField(
            'self',
            symmetrical=False,
            related_name="before_nodes",
            blank=True)
    name = models.CharField(max_length=128, default='')
    job = models.ForeignKey(
            'Job',
            models.SET_NULL,
            related_name="nodes",
            blank=True,
            null=True)
    application = models.ForeignKey(
            'App',
            models.SET_NULL,
            related_name="nodes",
            blank=True,
            null=True)
    automatically_added = models.BooleanField(default='False')
    listen_port = models.IntegerField(default=None, blank=True, null=True)

    def type_name(self):
        return self.node_type.name

    def to(self):
        to_nodes = []
        for n in self.next_nodes.all():
            to_nodes.append(n.name)
        return to_nodes

    def __str__(self):
        return '%s' % (self.name)

    # nodeが始端ノードであるか判定
    def is_source(self):
        num = self.before_nodes.count()
        if num == 0:
            return True
        return False

    # ノードタイプがセンサ系か否か
    # センサ系ならノード名文字列を、そうでなければNullを返す
    def sensor_name(self):
        if self.node_type is not None:
            if self.node_type.name in [
                    "StubSenseHatSource",
                    "SenseHatSource",
                    "PiCameraSource"]:
                return self.node_type.name
        return None
