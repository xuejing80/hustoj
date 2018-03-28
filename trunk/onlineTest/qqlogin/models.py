# encoding: utf-8
from django.db import models
from auth_system.models import MyUser

class OAuthQQ(models.Model):
    """QQ and User Bind"""
    user = models.ForeignKey(MyUser)   # 关联用户信息表
    qq_openid = models.CharField(max_length=64)   # QQ的关联OpenID

    # def __str__(self):
    #    return self.user

# Create your models here.
