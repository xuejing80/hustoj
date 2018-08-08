import argparse
import codecs
import json
import os
import random
import re
import shutil
import string
import zipfile
import cgi
import operator
from operator import itemgetter, attrgetter
from django.apps import apps
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.detail import DetailView
from mooc.forms import ResourceAddForm
from mooc.models import Resource,Week,Type
from judge.models import ClassName
from work.models import MyHomework,BanJi
from auth_system.models import MyUser
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
# Create your views here.

@login_required()
def ajax_add_course(request):
    serial_number = request.POST['serial_number']
    user = request.user
    id = 257    
    banji = BanJi.objects.get(pk=id)
    if serial_number == '12345':
        banji_r = BanJi.objects.filter(id=id, students=user)
        if any(banji_r) == True:
            return HttpResponse(json.dumps({'result':0,'repeat':1}))       # 学生已加入该班级
        banji.students.add(user)
        return HttpResponse(json.dumps({'result':0,'repeat':0}))

@login_required()
def add_course(request):
    return render(request,'add_course.html')

@login_required()
def get_courser_name(request):
    user = request.user
    coursers = ClassName.objects.all()
    array = {}
    if user.groups.all()[0].name == '老师':
        for courser in coursers:
            array[courser.id]=courser.name
    if user.groups.all()[0].name == '学生':
        banjis = BanJi.objects.filter(students=user)
        for banji in banjis:
            array[banji.courser.id] = banji.courser.name
    array = json.dumps(array)
    return HttpResponse(array)

@login_required()
def add_type(request):
    type = Type(name=request.POST['name'])
    type.save()
    return HttpResponse(1)

@login_required()
def type_resource(request):
    types = Type.objects.all()
    return render(request,'resource_type.html',{'types':types})
    
@login_required()
def list_course(request,id):
    user = request.user
    courser =  get_object_or_404(ClassName, pk=id)
    resources = Resource.objects.filter(courser=courser)
    weeks = Week.objects.all()
    banjis = BanJi.objects.filter(students=user,courser=courser)
    array = []
    array_w = []
    array_wt = []
    count = 0
    if user.is_admin == True or user.groups.all()[0].name == '老师':
        for week in weeks:
            resource_wt = Resource.objects.filter(week=week, courser=courser)
            if any(resource_wt) == True:
                array_wt.append(week)
        return render(request,'course_list.html', {'courser':courser,'weeks':array_wt,'resources':resources})
   
    if user.groups.all()[0].name == '学生':
        for week in weeks:
            ##resource_c = Resource.objects.filter(courser = courser)
            resource_w = Resource.objects.filter(week = week, courser = courser)
            for resource in resource_w:
                if (resource.creater.is_admin == True)&(week not in array_w):
                    array_w.append(week)
                
        if any(resource_w) == True:
            for resource in resource_w:         #不同的老师开了同一门课程的课，学生只显示自己班级老师对这门课创建的资源
                for banji in banjis:
                    if (banji.teacher == resource.creater)&(week not in array_w):  
                        array_w.append(week)

        for resource in resources:
            if (resource.creater.is_admin == True)&(resource not in array):
                array.append(resource)
                array.sort(key = attrgetter('num'))
        for resource in resources:
            for banji in banjis:                    #不同的老师开了同一门课程的课，学生只显示自己班级老师对这门课创建的资源
                if (banji.teacher == resource.creater)&(resource not in array):
                    array.append(resource)
                    array.sort(key = attrgetter('num'))
        for banji in banjis:                        #防止学生通过地址访问任意课程列表
            if banji.courser == courser:
                count = count + 1
        if count != 0:
            return render(request,'course_list.html', {'courser':courser,'weeks':array_w,'resources':array})   
        else:
            raise PermissionDenied

@login_required()
def resource_show(request,id):
    user = request.user
    resource = Resource.objects.get(pk=id)
    count = 0
    if user.groups.all()[0].name == '老师':
        return render(request, 'show_resource.html', context={'resource':resource})
    if user.groups.all()[0].name == '学生':
        banjis = BanJi.objects.filter(students=user)
        for banji in banjis:
            if ((banji.courser == resource.courser) and (banji.teacher == resource.creater)) or resource.creater.is_admin:
                count = count + 1
        if count != 0:
            if resource.type.name != '在线视频':
                return HttpResponseRedirect(resource.link)
            else:
                return render(request, 'show_resource.html', context={'resource':resource})
        else:
            raise PermissionDenied

@login_required()
def list_resource(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    resources = Resource.objects.all()
    classnames = ClassName.objects.all()
    return render(request, 'resource_list.html', context={'resources':resources,'classnames':classnames,'position':'resource_list','title':'资源库'})

class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resource_detail.html'
    context_object_name = 'resource'

    def get_context_data(self, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(**kwargs)
        '''
        str = ''
        for point in self.object.knowledgePoint2.all():
            str += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '\n'
        
        context['knowledge_point'] = str
        '''
        context['title'] = '选择题“' + self.object.title + '”的详细信息'
        return context

@login_required()
def add_resource(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    if request.method == 'POST':
        form = ResourceAddForm(request.POST)
        print(request.POST.dict())
        if form.is_valid():
            resource = form.save(user=request.user)
            old_path = '/home/judge/resource/' + request.POST['random_name'] + request.POST['file_name']
            print('a')
            print(old_path)
            #shutil.move(old_path, '/home/judge/resource/')
            print('b')
            #os.rename(old_path,
                      #'/home/judge/resource/' + str(resource.id) +'-'+ str(resource.creation_time) + request.POST['file_name'])
            #shutil.rmtree('/tmp/' + request.POST['random_name'])
            return redirect(reverse("resource_detail", args=[resource.id]))
    else:
        form = ResourceAddForm()
        print('ccc')
    return render(request, 'resource_add.html', {'form': form, 'title': '添加资源'})

@login_required()
def update_resource(request, id):
    resource = get_object_or_404(Resource, pk=id)
    if request.user != resource.creater and request.user.is_admin!=True:
        raise PermissionDenied
    else:
        initial = {
               'num': resource.num,
               'title': resource.title,
               'type': resource.type, 
               'courser': resource.courser,
               'week': resource.week,
               'link': resource.link, 
               'creater': resource.creater,
               }  # 生成表单的初始化数据
        if request.method == "POST":  # 当提交表单时
            form = ResourceAddForm(request.POST)
            if form.is_valid():
                resource = form.save(user=request.user, id=id)
                return redirect(reverse("resource_detail", args=[resource.id]))
        return render(request, 'resource_add.html', {'form': ResourceAddForm(initial=initial)})

@login_required()
def del_resource(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        for pk in ids:
            resources = Resource.objects.filter(pk=pk)
        for resource in resources:
            if request.user == resource.creater:
                resource.delete()
                return HttpResponse(1)
            else:
                return HttpResponse(0) 
    else:
        return HttpResponse(0)

@login_required()
def get_Resource(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    json_data = {}
    kwargs = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    if request.GET['my'] == 'true' and not request.user.is_superuser:
        kwargs['creater'] = request.user
    if classname != '0':
        kwargs['courser__id'] = classname
    if 'search' in request.GET:
        kwargs['name__icontains'] = request.GET['search']
    resources = Resource.objects.filter(**kwargs)  #筛选
    #####json_data['total'] = resources.count()
    try:
        sort = request.GET['sort']                 
    except MultiValueDictKeyError:
        sort = 'pk'
    if request.GET['order'] == 'desc':
        sort = '-' + sort                          #排序
    for resource in resources.order_by(sort)[offset:offset + limit]:
        title = cgi.escape(resource.title)
        recode = {
                  'title': resource.title, 
                  'id': resource.id,
                  'type': resource.type.name, 
                  'creater': resource.creater.username, 
                  'creation_time': resource.creation_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'courser': resource.courser.name,
                  'week': resource.week.name
                  }
        if resource.creater == request.user or request.user.is_admin:
            recodes.append(recode)
    json_data['total'] = resources.count()
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))

@login_required()
def uploud_file(request):
    """
    验证上传的文件是否符合规范
    :param request: 上传文件请求
    :return: 以json格式返回文件验证信息
    """
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    try:
        file = request.FILES['file_upload']
        print('1')
        count = in_count = out_count = 0
        random_name = ''.join(random.sample(string.digits + string.ascii_letters * 10, 8))  # 生成随机字符串作为文件名保存文件，防止相同文件名冲突
        tempdir = os.path.join('/var/www/html/static', 'upload')
        print(tempdir)
        print('2')
        filename1,filename2 = os.path.splitext(file.name)
        filename = os.path.join(tempdir, random_name + filename2)
        link = os.path.join('/static/upload', random_name + filename2)
        print(filename)
        destination = open(filename, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        print('3')
        print(random_name)
        print(filename)
    except Exception as e:
        logger.exception("保存用户资源失败：用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict()))
        return HttpResponse(
            json.dumps({'result': 0, 'info': '上传用户资源文件时遇到错误，请稍后再试，或联系管理员老师'}))
    return HttpResponse(json.dumps({"result": 1, 'info': random_name, 'filename': link}))
