from rest_framework import serializers

from .models import Agent, App, User


class HeartbeatSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    capability = serializers.CharField()
    agent_type = serializers.CharField()
    in_use = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
    longtitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    def create(self, validated_data):
        """
        ここにheartbeat受信時の処理を書く
        * request内容読み込み、Agentモデルのインスタンス作成/更新
        * responseを返す
            * Appモデルのインスタンスのうち、agentの割当オファーをしているもの
              を探す
            * heartbeatを送ってきたagentにオファーをだすAppを決める
            * AppのIDを読み取る
        """
        return False


class AcceptSerializer(serializers.Serializer):
    agent_id = serializers.IntegerField()
    app_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()

    def create(self, validated_data):
        return validated_data
