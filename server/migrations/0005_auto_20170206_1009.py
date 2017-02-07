# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-06 10:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20170206_0759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='hold',
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=models.IntegerField(choices=[(1, 'idle'), (2, 'accept_pending'), (3, 'running'), (4, 'stop_pending'), (5, 'stopped')], default=1, verbose_name='Job Status'),
        ),
        migrations.AlterField(
            model_name='app',
            name='status',
            field=models.IntegerField(choices=[(1, 'idle'), (2, 'launching'), (3, 'running'), (4, 'stopping'), (5, 'stopped')], default=1, verbose_name='App Status'),
        ),
    ]
