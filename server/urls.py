from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from server import views

router = routers.SimpleRouter()


urlpatterns = [
    url(r'^form', views.upload_file, name='upload_file'),
    url(r'^complete/', views.complete, name='complete'),
    url(r'^heartbeat$', views.heartbeat_response),
    url(r'^ctrl_apps', views.ctrl_apps),
    url(r'^job/(?P<job_id>.+)/accept', views.job_accept_request),
    url(r'^job/(?P<job_id>.+)', views.job_request)
]

urlpatterns += staticfiles_urlpatterns()
