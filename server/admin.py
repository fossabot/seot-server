from django.contrib import admin

from .models.agent import Agent
from .models.app import App
from .models.job import Job
from .models.node import Node
from .models.nodetype import NodeType


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = (
            'id', 'user_id', 'ip_addr', 'active', 'latest_heartbeat_at',
            'dpp_listen_port')


@admin.register(NodeType)
class NodeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'application_id')


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', '_next_nodes',
                    'job', 'args', 'listen_port')

    def _next_nodes(self, obj):
        if hasattr(obj, 'next_nodes'):
            return ','.join([node.name for node in obj.next_nodes.all()])
        else:
            return "this node has no next nodes."
