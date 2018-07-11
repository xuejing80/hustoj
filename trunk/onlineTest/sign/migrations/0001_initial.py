# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-04-22 23:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('work', '0004_myhomework_allow_random'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=1024)),
                ('has_signed_count', models.IntegerField()),
                ('all_student_count', models.IntegerField()),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('started_time', models.DateTimeField()),
                ('closed_time', models.DateTimeField()),
                ('banji', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banji', to='work.BanJi')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sign.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]