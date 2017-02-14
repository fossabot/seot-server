from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from server import views

urlpatterns = [
    url(r'^heartbeat$', views.heartbeat_response),
    url(r'^job/(?P<job_id>.+)/stop', views.job_stop_request),
    url(r'^job/(?P<job_id>.+)/accept', views.job_accept_request),
    url(r'^job/(?P<job_id>.+)', views.job_request),
    url(r'^app/(?P<app_id>.+)/launch',
        views.app_launch_request, name='app_launch'),
    url(r'^app/(?P<app_id>.+)/stop',
        views.app_stop_request, name='app_stop'),
]

urlpatterns += staticfiles_urlpatterns()
