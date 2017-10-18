#coding=utf-8
import hashlib
import json
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from . import models

TOKEN = 'njuptc'
def index(request):
    """
    所有的消息都会先进入这个函数进行处理，函数包含两个功能，
    微信接入验证是GET方法，
    微信正常的收发消息是用POST方法。
    """
    if request.method == "GET":
        if request.GET :
            signature = request.GET.get("signature", None)
            timestamp = request.GET.get("timestamp", None)
            nonce = request.GET.get("nonce", None)
            echostr = request.GET.get("echostr", None)
            
            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            #print("handle/GET func: hashcode, signature: ", hashcode, signature)

            if hashcode == signature:
                return HttpResponse(echostr)
            else:
                return HttpResponse("")
        else:
            return HttpResponse("hello, this is handle view")

#def index(request):
#    return HttpResponse('Hello,world!')

