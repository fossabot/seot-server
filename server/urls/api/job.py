from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from server.views.api.job_view import JobView

urlpatterns = [
    url(r'^job/(?P<job_id>.+)/stop', JobView.stop),
    url(r'^job/(?P<job_id>.+)/accept', JobView.accept),
    url(r'^job/(?P<job_id>.+)', JobView.get),
]

urlpatterns += staticfiles_urlpatterns()
