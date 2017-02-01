from django.conf.urls import url
from rest_framework import routers
from server import views

router = routers.SimpleRouter()


urlpatterns = [
    url(r'^form', views.upload_file, name='upload_file'),
    url(r'^complete/', views.complete, name='complete'),
    url(r'^heartbeat$', views.heartbeat_response),
    url(r'^job/(?P<job_id>.+)', views.job_request)
]
