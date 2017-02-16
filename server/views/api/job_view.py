import json
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from server.models.app_status import AppStatus
from server.models.job import Job
from server.models.job_status import JobStatus
from server.models.node import Node
from server.models.request_status import RequestStatus
from server.models.uuid import UUID4
from server.views.json_view import JSONResponse


class JobView:
    @staticmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def get(request, job_id):

        if UUID4.validate(job_id) is None:
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
            response = {
                "error": "Job does not exist.",
            }
            return JSONResponse(response, status=400)

    @staticmethod
    def _post(request, job_id, request_status):
        if UUID4.validate(job_id) is None:
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
            response = {
                "error": "Job does not exist."
            }
            return JSONResponse(response, status=400)

    @classmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def accept(cls, request, job_id):
        return cls._post(request, job_id, RequestStatus.accept.value)

    @classmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def stop(cls, request, job_id):
        return cls._post(request, job_id, RequestStatus.stop.value)
