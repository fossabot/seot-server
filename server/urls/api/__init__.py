from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('server.urls.api.heartbeat')),
    url(r'^app/', include('server.urls.api.app')),
    url(r'^job/', include('server.urls.api.job')),
]
