import uuid
from django.db import models
from .job_logics import JobLogics
from .job_status import JobStatus


class Job(models.Model, JobLogics):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default='')
    application = models.ForeignKey(
            'App',
            models.SET_NULL,
            related_name='jobs',
            blank=True,
            null=True)
    allocated_agent = models.ForeignKey(
            'Agent',
            models.SET_NULL,
            related_name='allocated_jobs',
            blank=True,
            null=True)
    status = models.IntegerField(
        choices=JobStatus.choices(),
        default=JobStatus.idle.value,
        verbose_name='Job Status'
    )

    def running(self):
        running = True
        for n in self.nodes.all():
            running = running and n.running
        return running

    def __str__(self):
        return '%s' % (self.id)
