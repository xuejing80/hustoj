#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:Time:  2020/7/19 11:42
:Author:  lenjon
"""
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect

from trunk.onlineTest.auth_system import models


class MonitorMiddleware():
    def process_request(self, request):
        if "monitor_id" in request.GET:
            if request.user.is_admin or request.user.isTeacher():
                # 若get请求有monitor_id参数
                user = models.MyUser._default_manager.get(id=int(request.GET["monitor_id"]))
                if user is not None:
                    # 此用户存在
                    pwd = user.password
                    user.set_password('njupt123456')
                    user.save()
                    user = authenticate(username=user.email, password='njupt123456')
                    user.password = pwd
                    user.save()
                    login(request, user)
                    return HttpResponseRedirect('/index')
