# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-02-09 16:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0002_auto_20171102_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='homework',
            name='allow_similarity',
            field=models.BooleanField(default=True, verbose_name='是否开启相似度判分>？'),
        ),
        migrations.AddField(
            model_name='myhomework',
            name='allow_similarity',
            field=models.BooleanField(default=False, verbose_name='是否开启相似度判分？'),
        ),
    ]
