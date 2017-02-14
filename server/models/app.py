import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from .status import AppStatus


class App(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(User, related_name="apps", blank=True, null=True)
    define_file = models.FileField(upload_to='uploads/app_define_files/',
                                   blank=True, null=True)
    upload_time = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(
        choices=AppStatus.choices(),
        default=AppStatus.idle.value,
        verbose_name='App Status'
    )

    def download_link_tag(self):
        if self.yaml_file:
            return format_html(
                    '<a href="{}">download file<>',
                    self.define_file.url)
        else:
            return "No attachment"

    def __str__(self):
        return '%s' % (self.name)
