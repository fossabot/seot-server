# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-02-03 10:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_auto_20170203_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='next_nodes',
            field=models.ManyToManyField(blank=True, null=True, related_name='before_nodes', to='server.Node'),
        ),
    ]