from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from server.views.app_view import AppView

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^upload', AppView.upload, name='upload_file'),
    url(r'^$', AppView.get, name='toppage'),
]
