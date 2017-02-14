from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from server import views

urlpatterns = [
    url(r'^app/(?P<app_id>.+)/launch',
        views.app_launch_request, name='app_launch'),
    url(r'^app/(?P<app_id>.+)/stop',
        views.app_stop_request, name='app_stop'),
]

urlpatterns += staticfiles_urlpatterns()
