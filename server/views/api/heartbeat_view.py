from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from .models.agent import Agent
from .models.job import Job
from .models.status import AppStatus, JobStatus
from .views import JSONResponse


class HeartbeatView:

    @transaction.atomic
    @csrf_exempt
    @api_view(['POST'])
    @parser_classes((JSONParser, ))
    def post(self, request):
        data = JSONParser().parse(request)

        try:
            user = User.objects.get(username=data['user_name'])
            agent, created = Agent.objects.get_or_create(
                    id=data['agent_id'],
                    user_id=user.id,
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    ip_addr=data['facts']['ip'],
                    hostname=data['facts']['hostname'])

            agent.update_nodetypes(data['nodes'])
            agent.update_latest_heartbeat_at(timezone.now())
            agent.save()

            job = Job.objects.get(allocated_agent_id=agent.id)
            if job.application.status == AppStatus.launching.value and\
                    job.status == JobStatus.idle.value:
                # AppがlaunchingでJobがidleのとき
                response = {
                    "run": job.id,
                    "kill": None,
                }
                job.status = JobStatus.accept_pending.value
                job.save()
                return JSONResponse(response, status=200)
            elif job.application.status == AppStatus.stopping.value and\
                    job.status == JobStatus.running.value:
                # AppがstoppingでJobがrunnningのとき
                response = {
                    "run": None,
                    "kill": job.id,
                }
                job.status = JobStatus.stop_pending.value
                job.save()
                return JSONResponse(response, status=200)
            else:
                response = {
                    "run": None,
                    "kill": None,
                }
                return JSONResponse(response, status=200)
        except Job.DoesNotExist:
            # ジョブがない場合のレスポンス
            response = {
                "run": None,
                "kill": None,
            }
            return JSONResponse(response, status=200)
        except User.DoesNotExist:
            # ユーザが存在しない場合
            return JSONResponse({}, status=400)
