# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-12 10:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0005_auto_20180412_1004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='rname',
        ),
    ]
