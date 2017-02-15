from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class JSONView:
    @staticmethod
    def response(data, status):
        content = JSONRenderer().render(data)
        kwargs = {}
        kwargs['content_type'] = 'application/json'
        kwargs['status'] = status
        return HttpResponse(content, **kwargs)
