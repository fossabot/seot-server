import json
from decimal import Decimal
from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)


class App(models.Model):
    app_id = models.CharField(max_length=128, default='0')
    name = models.CharField(max_length=128, blank=True)


class Agent(models.Model):
    user_id = models.CharField(max_length=128, default='0')
    agent_id = models.CharField(max_length=128, default='0')
    device_type = models.CharField(max_length=32, default='sensor')
    created_at = models.DateTimeField(auto_now_add=True)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    default=Decimal('0.0'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   default=Decimal('0.0'))
    dpp_listen_port = models.IntegerField(default=51423)

    name = models.CharField(max_length=128, blank=True)
#    user = models.ForeignKey(User, null=True, blank=True,
#                             related_name="owned_agent")
    capability = models.CharField(max_length=1024, blank=True)
    in_use = models.BooleanField(default=0, blank=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    def setcapability(self, capability):
        self.capability = json.dumps(capability)

    def getcapability(self):
        return json.loads(self.capability)

# Create your models here.
