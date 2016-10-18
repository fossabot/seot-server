from rest_framework import serializers

from .models import Agent, App, User


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('user_id', 'agent_id', 'device_type', 'longitude',
                  'latitude', 'dpp_listen_port')


class HeartbeatSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    agent_id = serializers.CharField()
    device_type = serializers.CharField()
    longtitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
        agent, created = Agent.objects.get_or_create(
                pk=validated_data.get('agent_id')
        )
        if created:
            agent.name = validated_data.get('agent_name')
            agent.owner = User.objects.get(pk=validated_data.get('user_id'))
            agent.capability = validated_data.get('capability')
            agent.agent_type = validated_data.get('agent_type')
#        agent.in_use = validated_data.get('in_use')
        agent.latest_heartbeat_at = validated_data.get('timestamp')
        agent.longtitude = validated_data.get('longtitude')
        agent.latitude = validated_data.get('latitude')
        agent.in_use = False
        agent.save()
        """
        ここにheartbeat受信時の処理を書く
        * request内容読み込み、Agentモデルのインスタンス作成/更新
        * responseを返す
            * Appモデルのインスタンスのうち、agentの割当オファーをしているもの
              を探す
            * heartbeatを送ってきたagentにオファーをだすAppを決める
            * AppのIDを読み取る
        """
        return agent

"""
class AcceptSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    app_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()

    def create(self, validated_data):
        return validated_data
"""
