from django.conf.urls import url
from server import views

urlpatterns = [
    url(r'^form', views.upload_file, name='upload_file'),
    url(r'^complete/', views.complete, name='complete'),
    url(r'^heartbeat$', views.heartbeat_response),
]
