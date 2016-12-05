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

        nodes_data = self.validated_data.pop("nodes")
        self.nodes_create_and_add(agent, nodes_data)
        return agent

    def nodes_create_and_add(self, agent, nodes_data):
        for node_data in nodes_data:
            node_type, created = NodeType.objects.\
                    get_or_create(name=str(node_data))
            node_type.save()
            agent.available_node_types.add(node_type)
