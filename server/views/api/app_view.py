from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from server.models.app import App
from server.models.app_status import AppStatus
from server.models.request_status import RequestStatus
from server.models.uuid import UUID4
from server.views.json_view import JSONView


class AppView:
    @classmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def launch(cls, request, app_id):
        try:
            app = App.objects.get(id=app_id)
            if app.launch_jobs():
                cls._post(
                        request, app_id, RequestStatus.accept.value)
        except ObjectDoesNotExist:
            print("app DoesNotExist")
        finally:
            return HttpResponseRedirect(reverse('toppage'))

    @classmethod
    @transaction.atomic
    @csrf_exempt
    @parser_classes((JSONParser, ))
    def stop(cls, request, app_id):
        cls._post(request, app_id, RequestStatus.stop.value)
        return HttpResponseRedirect(reverse('toppage'))

    @staticmethod
    def _post(request, app_id, request_status):
        # uuidがuuid4に準拠しているかどうか
        if UUID4.validate(app_id) is None:
            return JSONView.response({}, status=400)

        try:
            app = App.objects.get(id=app_id)
            if request_status == RequestStatus.accept.value:
                app.status = AppStatus.launching.value
            elif request_status == RequestStatus.stop.value:
                app.status = AppStatus.stopping.value
            app.save()
            response = {
                "app_id": str(app.id),
                "app_status": str(app.status)
            }
            return JSONView.response(response, status=200)
        except App.DoesNotExist:
            response = {
                "error": "App does not exist.",
            }
            return JSONView.response(response, status=400)
