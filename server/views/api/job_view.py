import json
import re

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

from .models.app_status import AppStatus
from .models.job import Job
from .models.job_status import JobStatus
from .models.node import Node
from .view import JSONResponse, RequestStatus


class JobView:

    # uuid4に準拠しているかどうかを返す
    def _validate_uuid4(self, uuid):
        return re.match(
                "[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}\
    -[89ab][0-9a-f]{3}-[0-9a-f]{12}", uuid)

    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def get(self, job_id):

        if self._validate_uuid4(job_id) is None:
            return JSONResponse({}, status=400)

        try:
            job = Job.objects.get(id=job_id)
            nodes = []
            for n in job.nodes.all():
                node = {
                    "name": n.name,
                    "type": n.type_name(),
                    "to": n.to()
                }
                if n.args:
                    node["args"] = json.loads(n.args)
                nodes.append(node)

            response = {
                "job_id": str(job.id),
                "application_id": str(job.application_id),
                "nodes": nodes
            }
            return JSONResponse(response, status=200)
        except Job.DoesNotExist:
            return JSONResponse({}, status=400)

    def _post(self, request, job_id, request_status):

        if self._validate_uuid4(job_id) is None:
            return JSONResponse({}, status=400)

        try:
            job = Job.objects.get(id=job_id)
            running_nodes = Node.objects.filter(
                job_id=job.id,
                job__allocated_agent_id=job.allocated_agent_id
            )
            for n in running_nodes:
                if request_status == RequestStatus.accept.value:
                    n.running = True
                elif request_status == RequestStatus.stop.value:
                    n.running = False
                n.save()

            nodes = []
            for n in job.nodes.all():
                node = {
                    "name": n.name,
                    "type": n.type_name(),
                    "args": n.args,
                    "to": n.to()
                }
                nodes.append(node)

            # acceptリクエストが来て、Jobステータスがaccept_pendingのとき
            # Jobステータスをrunnningに
            if request_status == RequestStatus.accept.value and\
                    job.status == JobStatus.accept_pending.value:
                job.status = JobStatus.running.value
                job.save()
                # appの全jobがrunnningのとき、AppStatusをrunnningに
                if not job.application.jobs.exclude(
                        status=JobStatus.running.value).exists():
                    job.application.status = AppStatus.running.value
                    job.application.save()
            # stopリクエストが来て、jobステータスがstop_pendingのとき
            # jobステータスをidleに
            elif request_status == RequestStatus.stop.value and\
                    job.status == JobStatus.stop_pending.value:
                job.status = JobStatus.idle.value
                job.save()
                # appの全jobがidleのとき、AppStatusをidleに
                if not job.application.jobs.exclude(
                        status=JobStatus.idle.value).exists():
                    job.application.status = AppStatus.idle.value
                    job.application.save()
                    job.application.clear_jobs()

            response = {
                "job_id": str(job.id),
                "application_id": str(job.application_id),
                "nodes": nodes
            }
            return JSONResponse(response, status=200)
        except Job.DoesNotExist:
            return JSONResponse({}, status=400)

    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def accept(self, request, job_id):
        return self._post(request, job_id, RequestStatus.accept.value)

    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def stop(self, request, job_id):
        return self._post(request, job_id, RequestStatus.stop.value)
