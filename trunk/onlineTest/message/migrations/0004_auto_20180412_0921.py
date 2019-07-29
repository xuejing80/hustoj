# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-12 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0003_auto_20180412_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='isread',
            field=models.BooleanField(default=False, verbose_name='是否读过'),
        ),
        migrations.AddField(
            model_name='message',
            name='message',
            field=models.CharField(blank=True, max_length=512, verbose_name='消息'),
        ),
        migrations.AddField(
            model_name='message',
            name='messagetype',
            field=models.PositiveSmallIntegerField(choices=[(0, '系统消息'), (1, '邀请消息'), (2, '关注消息'), (3, '问题状态消息')], default=0, verbose_name='消息类型'),
        ),
        migrations.AddField(
            model_name='message',
            name='questionId',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='rid',
            field=models.PositiveIntegerField(default=1, verbose_name='消息接收者'),
        ),
        migrations.AddField(
            model_name='message',
            name='rname',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='消息接收者姓名'),
        ),
        migrations.AddField(
            model_name='message',
            name='sid',
            field=models.PositiveIntegerField(default=1, verbose_name='消息发送者'),
        ),
        migrations.AddField(
            model_name='message',
            name='sname',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='消息发送者姓名'),
        ),
    ]