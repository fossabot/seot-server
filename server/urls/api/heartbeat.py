from django.conf.urls import url
from server.views.api.heartbeat_view import HeartbeatView

urlpatterns = [
    url(r'^heartbeat$', HeartbeatView.post),
]
