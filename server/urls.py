from django.conf.urls import url
from server import views

urlpattern = [
    url(r'^heartbeat/$', views.heartbeat_response),
    url(r'^accept/$', views.accept_response),
]
