# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-16 14:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0008_auto_20180414_2143'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='questionId',
            new_name='objId',
        ),
    ]