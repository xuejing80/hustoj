# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-15 16:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0003_leave_cause'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leave',
            name='user',
        ),
    ]
