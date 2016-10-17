import json
from decimal import Decimal
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=32)


class App(models.Model):
    name = models.CharField(max_length=32)


class Agent(models.Model):
    name = models.CharField(max_length=128)
    owner = models.ForeignKey(User, null=True, related_name="owned_agent")
    capability = models.CharField(max_length=1024)
    agent_type = models.CharField(max_length=32)
    in_use = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    latest_heartbeat_at = models.DateTimeField(auto_now=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                    default=Decimal('0.0'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                   default=Decimal('0.0'))

    def setcapability(self, capability):
        self.capability = json.dumps(capability)

    def getcapability(self):
        return json.loads(self.capability)

# Create your models here.
