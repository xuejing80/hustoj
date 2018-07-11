# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-10-18 21:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('judge', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('work', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='homework_answer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='work.HomeworkAnswer'),
        ),
        migrations.AddField(
            model_name='problem',
            name='classname',
            field=models.ManyToManyField(to='judge.ClassName', verbose_name='所属课程'),
        ),
        migrations.AddField(
            model_name='problem',
            name='creater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='problem',
            name='knowledgePoint1',
            field=models.ManyToManyField(to='judge.KnowledgePoint1', verbose_name='一级知识点'),
        ),
        migrations.AddField(
            model_name='problem',
            name='knowledgePoint2',
            field=models.ManyToManyField(to='judge.KnowledgePoint2', verbose_name='二级知识点'),
        ),
        migrations.AddField(
            model_name='knowledgepoint2',
            name='upperPoint',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.KnowledgePoint1', verbose_name='上级课程'),
        ),
        migrations.AddField(
            model_name='knowledgepoint1',
            name='classname',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.ClassName', verbose_name='所属课程'),
        ),
        migrations.AddField(
            model_name='choiceproblem',
            name='classname',
            field=models.ManyToManyField(to='judge.ClassName', verbose_name='所属课程'),
        ),
        migrations.AddField(
            model_name='choiceproblem',
            name='creater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='choiceproblem',
            name='knowledgePoint1',
            field=models.ManyToManyField(to='judge.KnowledgePoint1', verbose_name='一级知识点'),
        ),
        migrations.AddField(
            model_name='choiceproblem',
            name='knowledgePoint2',
            field=models.ManyToManyField(to='judge.KnowledgePoint2', verbose_name='二级知识点'),
        ),
    ]
