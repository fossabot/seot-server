from django.conf.urls import url
from server import views

urlpatterns = [
    url(r'^heartbeat/$', views.heartbeat_response),
]
