from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from server import views

router = routers.SimpleRouter()


urlpatterns = [
    url(r'^upload', views.upload_file, name='upload_file'),
    url(r'^$', views.ctrl_apps, name='ctrl_apps'),
]

urlpatterns += staticfiles_urlpatterns()
