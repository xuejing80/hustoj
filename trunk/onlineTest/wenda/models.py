#-*-conding:utf-8 -*_

from __future__ import unicode_literals
from django.db import models

from auth_system.models import MyUser
# Create your models here.

class Question(models.Model):
    asker = models.ForeignKey(MyUser, related_name='my_question', verbose_name="提问者")
    ques = models.CharField(u'问题', max_length=256, null=False)
    update_date = models.DateField(u'提问时间', auto_now_add=True)
    description = models.TextField(u'问题描述', null=True, blank=True)
    tag = models.CharField(u'问题标签', max_length=50, blank=True)
    praisenum = models.PositiveIntegerField(u'问题点赞数', default=0)

    def __str__(self):
        return self.ques



class Answer(models.Model):
    question = models.ForeignKey(
        Question, related_name='ques_answer', null=False, on_delete=models.CASCADE)
    answer = models.TextField(u'答案', null=True,blank=True)
    replier = models.ForeignKey(MyUser, related_name="my_answer", null=True)
    answer_date = models.DateField(u'回答时间', auto_now_add=True, null=True)
    praisenum = models.PositiveIntegerField(u'答案点赞数', default=0)
    def __str__(self):
        return self.answer

    class Meta:
        ordering = ['-praisenum']
		

class Collection(models.Model):
    owner = models.ForeignKey(MyUser, related_name="my_collection", verbose_name="收藏者", on_delete=models.CASCADE)
    questionId = models.PositiveIntegerField(u'收藏的问题id', blank=True)
    ansId = models.PositiveIntegerField(u'收藏的答案id', blank=True, null=True)
    collect_date = models.DateField(u'评论时间', auto_now_add=True, null=True)

    def __str__(self):
        return self.owner.username

class UploadInfo(models.Model):
    date = models.DateTimeField(u'上传时间', auto_now_add=True)
    ip = models.CharField(u'用户ip地址', max_length=25)
    uid = models.PositiveIntegerField(u'用户id')
    file_size = models.PositiveIntegerField(u'上传文件大小',default = 0)

class RecommendAns(models.Model):
    qid = models.PositiveIntegerField(u'问题的id')
    aid = models.PositiveIntegerField(u'答案的id')

