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
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.detail import DetailView
from mooc.forms import ResourceAddForm
from mooc.models import Resource,Week,Type
from judge.models import ClassName
from work.models import MyHomework,BanJi
from auth_system.models import MyUser
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

# Create your views here.

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

def add_type(request):
    type = Type(name=request.POST['name'])
    type.save()
    return HttpResponse(1)

def type_resource(request):
    types = Type.objects.all()
    return render(request,'resource_type.html',{'types':types})
    
def list_course(request,id):
    resources = Resource.objects.all()
    courser =  ClassName.objects.get(pk=id)
    weeks = Week.objects.all()
    array=[]
    array_w = []
    for week in weeks:
        resource_w = Resource.objects.filter(week = week,courser = courser)
        if any(resource_w) == True:
            array_w.append(week)
    for resource in resources:
        array.append(resource)
        array.sort(key = attrgetter('num'))
    return render(request,'course_list.html', {'courser':courser,'weeks':array_w,'resources':array,'title':courser.name})

def resource_show(request,id):
    resource = Resource.objects.get(pk=id)
    return render(request, 'show_resource.html', context={'resource':resource})

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

def add_resource(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied 
    if request.method == 'POST':
        form = ResourceAddForm(request.POST)
        if form.is_valid():
            resource = form.save(user=request.user)
            old_path = '/home/judge/resource/' + request.POST['random_name'] + request.POST['file_name']
            #shutil.move(old_path, '/home/judge/resource/')
            #os.rename(old_path,
                      #'/home/judge/resource/' + str(resource.id) +'-'+ str(resource.creation_time) + request.POST['file_name'])
            #shutil.rmtree('/tmp/' + request.POST['random_name'])
            return redirect(reverse("resource_detail", args=[resource.id]))
    else:
        form = ResourceAddForm()
    return render(request, 'resource_add.html', {'form': form, 'title': '添加资源'})

def update_resource(request, id):
    resource = get_object_or_404(Resource, pk=id)
    if request.user != resource.creater and request.user.is_admin!=True:
        raise PermissionDenied
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
    try:
        resources = Resource.objects.filter(**kwargs)  #筛选
    except Exception as err:
        print(err)
    json_data['total'] = resources.count()
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
