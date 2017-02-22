from django.conf.urls import url
from server.views.api.job_view import JobView

urlpatterns = [
    url(r'^(?P<job_id>.+)/stop', JobView.stop),
    url(r'^(?P<job_id>.+)/accept', JobView.accept),
    url(r'^(?P<job_id>.+)', JobView.get),
]
