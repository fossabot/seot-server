from django.contrib import admin

from .models import App, Agent, User


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    pass


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

# Register your models here.
