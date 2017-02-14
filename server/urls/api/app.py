from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from server.views.api.app_view import AppView

urlpatterns = [
    url(r'^app/(?P<app_id>.+)/launch',
        AppView.launch, name='app_launch'),
    url(r'^app/(?P<app_id>.+)/stop',
        AppView.stop, name='app_stop'),
]

urlpatterns += staticfiles_urlpatterns()
