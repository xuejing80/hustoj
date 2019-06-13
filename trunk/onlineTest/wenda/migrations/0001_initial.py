# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2019-05-05 13:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(blank=True, null=True, verbose_name='答案')),
                ('answer_date', models.DateField(auto_now_add=True, null=True, verbose_name='回答时间')),
                ('praisenum', models.PositiveIntegerField(default=0, verbose_name='答案点赞数')),
            ],
            options={
                'ordering': ['-praisenum'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('questionId', models.PositiveIntegerField(blank=True, verbose_name='收藏的问题id')),
                ('ansId', models.PositiveIntegerField(blank=True, null=True, verbose_name='收藏的答案id')),
                ('collect_date', models.DateField(auto_now_add=True, null=True, verbose_name='评论时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_collection', to=settings.AUTH_USER_MODEL, verbose_name='收藏者')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ques', models.CharField(max_length=256, verbose_name='问题')),
                ('update_date', models.DateField(auto_now_add=True, verbose_name='提问时间')),
                ('description', models.TextField(blank=True, null=True, verbose_name='问题描述')),
                ('tag', models.CharField(blank=True, max_length=50, verbose_name='问题标签')),
                ('praisenum', models.PositiveIntegerField(default=0, verbose_name='问题点赞数')),
                ('asker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_question', to=settings.AUTH_USER_MODEL, verbose_name='提问者')),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ques_answer', to='wenda.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='replier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_answer', to=settings.AUTH_USER_MODEL),
        ),
    ]
