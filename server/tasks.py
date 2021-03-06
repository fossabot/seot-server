from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from .models.agent import Agent


@shared_task
def check_timeout():
    print('timeout')
    delay = timedelta(seconds=10)
    for a in Agent.objects.filter(
            latest_heartbeat_at__lte=(timezone.now() - delay), active=True):
        a.active = False
        a.save()
