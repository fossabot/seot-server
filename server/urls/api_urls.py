from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from server import views

urlpatterns = [
    url(r'^heartbeat$', views.heartbeat_response),
    url(r'^job/(?P<job_id>.+)/accept', views.job_accept_request),
    url(r'^job/(?P<job_id>.+)', views.job_request)
]

urlpatterns += staticfiles_urlpatterns()
