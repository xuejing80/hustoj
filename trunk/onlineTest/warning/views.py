# -*- coding:utf-8 -*-
from django.shortcuts import render
import re
import json
from judge.models import ChoiceProblem
from warning.models import WarningData
from django.http import HttpResponse, Http404

def warning(request):
	user = request.user
	did = request.GET.get('id')

	if (did is None or isNum(did) == False):
		mydict = {"error":"请检查链接是否正确"}
		return render(request,'error.html',mydict)

	winfo = WarningData.objects.filter(id = did).first()
	if winfo is None:
		mydict = {"error":"请检查链接是否正确"}
		return render(request,'error.html',mydict)
	data = winfo.data
	tid = winfo.tid

	if user:
		if user.id:
			if str(user.id) != str(tid):
				mydict = {"error":"您没有查看的权限！"}
				return render(request,'error.html',mydict)
		else:
			mydict = {"error":"请先登录后再查看!"}
			return render(request,'error.html',mydict)

	else:
		mydict = {"error":"请先登录后再查看!"}
		return render(request,'error.html',mydict)
	chwresult = json.loads(data)
	orderdict = {}
	for key,value in chwresult.items():
		orderdict[key] = value['w']/value['t']
	orderids = sorted(orderdict.items(),key = lambda x:x[1],reverse = True)

	wids = chwresult.keys()
	choiceinfodict = ChoiceProblem.objects.in_bulk(wids)

	choiceinfolist = []
	for x in orderids:
	 	d = {'choice':choiceinfodict[int(x[0])],'count':chwresult[x[0]]}
	 	choiceinfolist.append(d)
	return render(request,'wchoice.html',{'data':choiceinfolist})

def isNum(value):
    try:
        int(value)
    except:
        return False
    else:
        return True