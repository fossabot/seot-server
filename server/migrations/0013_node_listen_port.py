# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-26 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_job_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='listen_port',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
