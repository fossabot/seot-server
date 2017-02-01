import logging

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from .models import Node, NodeType

logger = logging.getLogger(__name__)


class NodeSerializer(serializers.ModelSerializer):
    args_str = serializers.CharField(max_length=256, required=False)
    type = serializers.CharField(max_length=128)
    to = serializers.ListField(
                allow_null=True,
                required=False,
                child=serializers.CharField(
                    max_length=128,
                    required=False,
                    allow_blank=True,
                    allow_null=True),
                )

    class Meta:
        model = Node
        fields = ('name', 'args_str', 'type', 'to')

    def get_nodetype_from_name(self, node, type_name):
        try:
            node_type, created = NodeType.objects.\
                                 get_or_create(name=str(type_name))
            node_type.nodes.add(node)
            node_type.save()
        except ObjectDoesNotExist:
            print("object does not exist")

    def create(self, validated_data):
        if 'args_str' in validated_data:
            node = Node.objects.create(
                    name=self.validated_data.pop('name'),
                    args=self.validated_data.pop('args_str')
                    )
        else:
            node = Node.objects.create(
                    name=self.validated_data.pop('name'))
        self.get_nodetype_from_name(
                node, self.validated_data.pop("type"))
        return node
