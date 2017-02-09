from django.conf.urls import url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from server import views

router = routers.SimpleRouter()


urlpatterns = [
    url(r'^form', views.upload_file, name='upload_file'),
    url(r'^complete/', views.complete, name='complete'),
    url(r'ctrl_apps/', views.ctrl_apps, name='ctrl_apps'),
]

urlpatterns += staticfiles_urlpatterns()
