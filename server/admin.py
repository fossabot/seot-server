from django.contrib import admin

from .models import Agent, App, Job, Node, NodeType, User


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('app_id', 'name')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'user_id', 'ip_addr', 'latest_heartbeat_at')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name')


@admin.register(NodeType)
class NodeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'name', 'application_id')


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'to', 'job', 'application')
