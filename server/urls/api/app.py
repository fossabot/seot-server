from django.conf.urls import url
from server.views.api.app_view import AppView

urlpatterns = [
    url(r'^(?P<app_id>.+)/launch',
        AppView.launch, name='app_launch'),
    url(r'^(?P<app_id>.+)/stop',
        AppView.stop, name='app_stop'),
]
