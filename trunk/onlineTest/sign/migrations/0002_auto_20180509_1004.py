# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2018-05-09 10:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sign', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=512)),
            ],
        ),
        migrations.AddField(
            model_name='sign',
            name='status',
            field=models.SmallIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='leave',
            name='sign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sign.Sign'),
        ),
        migrations.AddField(
            model_name='leave',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
