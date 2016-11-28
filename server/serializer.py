import logging

from rest_framework import serializers

from .models import Agent, NodeType

logger = logging.getLogger(__name__)


class NodeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeType
        fields = ('name')


class AgentSerializer(serializers.ModelSerializer):
    nodes = serializers.ListField(child=serializers.CharField(max_length=128))

    class Meta:
        model = Agent
        fields = ('user_id', 'agent_id', 'longitude',
                  'latitude', 'busy', 'nodes')

    def create(self):
        nodes_data = self.validated_data.pop("nodes")
        agent = Agent.objects.create(**self.validated_data)
        for node_data in nodes_data:
            node_type, created = NodeType.objects.\
                    get_or_create(name=str(node_data))
            node_type.save()
            agent.available_node_types.add(node_type)
        return agent
