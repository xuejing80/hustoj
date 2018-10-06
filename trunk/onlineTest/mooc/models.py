from django.db import models
from auth_system.models import MyUser
from judge.models import ClassName

# Create your models here.

class Week(models.Model):
    name = models.CharField(verbose_name='周次数', max_length=30)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'week_name'
        verbose_name = '周次数'
        verbose_name_plural = '周次数'

class Type(models.Model):
    name = models.CharField(verbose_name='资源类型', max_length=30)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'type_name'
        verbose_name = '资源类型'
        verbose_name_plural = '资源类型'

class Resource(models.Model):
    num = models.TextField('序号',null=True,blank=True)
    id = models.AutoField('id',primary_key=True)
    title = models.TextField('资源标题',max_length=50)
    type = models.ForeignKey('mooc.Type', verbose_name='资源类型')
    link = models.TextField('资源链接',null=True,blank=True)
    creater = models.ForeignKey(MyUser,null=True,related_name='Resource_creater')
    creation_time = models.DateTimeField(auto_now=True,verbose_name='创建时间',blank=True, null=True)
    courser = models.ForeignKey('judge.ClassName', verbose_name='所属课程')
    week = models.ForeignKey('mooc.Week', verbose_name='周次数')

class Number(models.Model):
    ming_ma=models.IntegerField(verbose_name='明码', null=True, blank=True,default=0)
    an_ma=models.CharField(verbose_name='暗码', max_length=30,null=True, blank=True,default=0)
    user=models.ForeignKey(MyUser,null=True,related_name='Number_user')
    time=models.CharField(verbose_name='加入时间', max_length=100, null=True, blank=True,default=0)
    is_used=models.CharField(verbose_name='是否使用', max_length=30,blank=True, null=True,default='false')
    
