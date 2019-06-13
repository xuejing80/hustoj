from django.db import models
from auth_system.models import MyUser
# Create your models here.

class Message(models.Model):

    # 消息类型
    msgtype = (  
        (0, u'系统消息'),  
        (1, u'邀请消息'), 
        (2, u'关注消息'),
        (3, u'回答问题消息'), 
        (4, u'评论问题消息'),  
        (5, u'更新答案消息'),
    ) 


    sid = models.PositiveIntegerField(verbose_name="发送者id")
    rid = models.PositiveIntegerField(verbose_name="接收者id")
    message = models.CharField(max_length=1024, blank=True, null=True, verbose_name="消息")
    objId = models.PositiveIntegerField(blank=True, null=True)
    messagetype = models.PositiveSmallIntegerField(verbose_name='消息类型', choices=msgtype, default=0)
    date = models.DateField(u'消息发布时间', auto_now_add=True, null=True)
    isread = models.BooleanField(verbose_name='是否读过', default=False)

    def __str__(self):
        return self.message
