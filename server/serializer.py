import json
import logging

from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from .models import Agent, App, Node, NodeType

logger = logging.getLogger(__name__)


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('name', 'user')


class NodeSerializer(serializers.ModelSerializer):
    # 組み込み関数のtypeと識別子名が衝突してる
    # あとで直すか？
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


class NodeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeType
        fields = ('name')


class AgentSerializer(serializers.ModelSerializer):
    nodes = serializers.ListField(child=serializers.CharField(max_length=128))

    class Meta:
        model = Agent
        fields = ('user_id', 'agent_id', 'longitude',
                  'latitude', 'busy', 'nodes', 'ip_addr')

    def create(self, validated_data):
        nodes_data = self.validated_data.pop("nodes")
        agent = Agent.objects.create(**self.validated_data)
        self.nodes_create_and_add(agent, nodes_data)
        return agent

    def update(self, agent, validated_data):
        agent.user_id = validated_data.get('user_id', agent.user_id)
        agent.agent_id = validated_data.get('agent_id', agent.agent_id)
        agent.longitude = validated_data.get('longitude', agent.longitude)
        agent.latitude = validated_data.get('latitude', agent.latitude)
        agent.busy = validated_data.get('busy', agent.busy)
        agent.ip_addr = validated_data.get('ip_addr', agent.ip_addr)

        nodes_data = self.validated_data.pop("nodes")
        self.nodes_create_and_add(agent, nodes_data)

        agent.save()
        return agent

    def nodes_create_and_add(self, agent, nodes_data):
        agent.available_node_types.clear()
        for node_data in nodes_data:
            node_type, created = NodeType.objects.\
                    get_or_create(name=str(node_data))
            node_type.save()
            agent.available_node_types.add(node_type)
