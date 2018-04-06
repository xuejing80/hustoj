from django.shortcuts import render, HttpResponseRedirect, HttpResponse
#from django.urls import reverse # reverse url逆向解析
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from . import models
#from .form import * 
import json
import time
from django.conf import settings
from .oauth_client import OAuthQQ

def qq_login(request):
    oauth_qq = OAuthQQ(settings.QQ_APP_ID, settings.QQ_KEY, settings.QQ_RECALL_URL)
     #获取 得到Authorization Code的地址
    url = oauth_qq.get_auth_url()
     #重定向到授权页面
    return HttpResponseRedirect(url)


def qq_check(request): # 第三方QQ登录，回调函数
    request_code = request.GET.get('code')
    oauth_qq = OAuthQQ(settings.QQ_APP_ID, settings.QQ_KEY, settings.QQ_RECALL_URL)

     # 获取access_token
    access_token = oauth_qq.get_access_token(request_code)
    time.sleep(0.05) # 稍微休息一下，避免发送urlopen的10060错误
    open_id = oauth_qq.get_open_id()
   # print open_id

    # 检查open_id是否存在
    qq_open_id = models.OAuthQQ.objects.filter(qq_openid=str(open_id))
   # print qq_open_id
    if qq_open_id:
         # 存在则获取对应的用户，并登录
        user = qq_open_id[0].user.username
       # print user
        request.session['username'] = user
        return HttpResponseRedirect('/qqlogin/')
    else:
         # 不存在，则跳转到绑定用户页面
        infos = oauth_qq.get_qq_info() # 获取用户信息
        url = '%s?open_id=%s&nickname=%s' % (reverse('bind_account'), open_id, infos['nickname'])
        return HttpResponseRedirect(url)

# Create your views here.
