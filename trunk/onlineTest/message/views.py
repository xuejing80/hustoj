from django.shortcuts import render, HttpResponse
from wenda.views import DateEncoder
from message.models import *
import json
from auth_system.models import MyUser
from wenda.views import DateEncoder
# Create your views here.     

def createMsg(sid,rid,objId,message=None,messagetype=0):
    try:
        Message.objects.create(sid=sid,rid=rid,objId=objId,message=message,messagetype=messagetype)
        return True
    except:
        return False
    
# 跳转我的消息页面
def toMessage(request):
    message = Message.objects.filter(rid=request.user.id,isread=False).order_by('-date').values('id','sid','message','objId','messagetype','date')
    for m in message:
        m['sname'] = MyUser.objects.get(id=m['sid']).username
    return render(request,'message/message.html',{'message':message})

# 设置消息为已读消息
# 返回参数：1表示操作成功;0表示操作失败;2表示没有获取消息的id
def readMessage(request):
    mid = request.GET.get('mid',None)
    if mid != None:
        try:
            Message.objects.filter(id=mid).update(isread=True)
            mnum = request.session['mnum']
            request.session['mnum'] = mnum - 1
            return HttpResponse("1")
        except Exception as e:
            # print(str(e))
            return HttpResponse("0")
    else:
        return HttpResponse("2")

def loadMessage(request):
    message = Message.objects.filter(rid=request.user.id,isread=True).order_by('date').values('id','sid','message','objId','messagetype','date')
    for m in message:
        m['sname'] = MyUser.objects.get(id=m['sid']).username
    
    return HttpResponse(json.dumps(list(message), cls=DateEncoder), content_type="application/json")
