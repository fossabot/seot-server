from django.contrib import admin

from .models import Agent, App, Job, Node, NodeType, User


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'user_id', 'ip_addr', 'latest_heartbeat_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(NodeType)
class NodeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'name', 'application_id')


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', '_next_nodes',
                    'job', 'application', 'args')

    def _next_nodes(self, obj):
        if hasattr(obj, 'to'):
            return ','.join([node.name for node in obj.next_nodes.all()])
        else:
            return "this node has no next nodes."


# @admin.register(AppDefineFile)
# class AppDefineFileAdmin(admin.ModelAdmin):
#     list_display = ('name', 'upload_time', 'file_link')
