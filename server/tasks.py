from __future__ import absolute_import, unicode_literals
from datetime import datetime
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import utc
from .models.agent import Agent


@shared_task
def check_timeout():
    print('timeout')
    today = datetime.utcnow().replace(tzinfo=utc)
    delay = timedelta(seconds=10)
    for agent in Agent.objects.filter(latest_heartbeat_at__lte=today - delay):
        print(agent)
        agent.delete()
