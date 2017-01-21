# coding:utf-8
from django.contrib.auth.models import Group, AbstractUser
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import View
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.contrib import auth
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from .forms import VmaigUserCreationForm, VmaigPasswordRestForm, PasswordChangeForm
from .models import MyUser
import json
from django.http import HttpResponse, Http404
import logging
import re

# logger
logger = logging.getLogger(__name__)


class UserControl(View):
    def post(self, request, *args, **kwargs):
        # 获取要对用户进行什么操作
        slug = self.kwargs.get('slug')

        if slug == 'login':
            return self.login(request)
        elif slug == "logout":
            return self.logout(request)
        elif slug == "register":
            return self.register(request)
        elif slug == "changepassword":
            return self.changepassword(request)
        elif slug == "forgetpassword":
            return self.forgetpassword(request)
        elif slug == "resetpassword":
            return self.resetpassword(request)

        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        # 如果是get请求直接返回404页面
        raise Http404

    def login(self, request):
        errors = []
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            user = auth.authenticate(username=email, password=password)
        elif email:
            try:
                user = MyUser._default_manager.get(id_num=email)
                user = auth.authenticate(username=user.email, password=password)
            except:
                user = None
        else:
            user = None

        if user is not None:
            auth.login(request, user)
        else:
            errors.append("密码或者用户名不正确")

        mydict = {"errors": errors}
        return HttpResponse(json.dumps(mydict), content_type="application/json")

    def logout(self, request):
        if not request.user.is_authenticated():
            logger.error(u'[UserControl]用户未登录')
            raise PermissionDenied
        else:
            auth.logout(request)
            return HttpResponse('OK')

    def register(self, request: object) -> object:
        username = self.request.POST.get("username", "")
        password1 = self.request.POST.get("password1", "")
        id_num = self.request.POST.get('id_num', "")
        password2 = self.request.POST.get("password2", "")
        email = self.request.POST.get("email", "")

        form = VmaigUserCreationForm(request.POST)

        errors = []
        # 验证表单是否正确
        if form.is_valid():
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            title = u"欢迎注册计算机语言作业平台！"
            message = u"你好！ %s ,感谢注册计算机语言作业平台 ！\n\n" % (username) + \
                      u"请牢记以下信息：\n" + \
                      u"用户名：%s \n" % id_num + \
                      u"昵称：%s" % username + "\n" + \
                      u"邮箱：%s" % email + "\n" + \
                      u"网站：http://%s" % domain + "/test\n\n"
            from_email = 'fornjupt@163.com'
            try:
                send_mail(title, message, from_email, [email])
            except Exception as e:
                logger.error(u'[UserControl]用户注册邮件发送失败:[%s]/[%s]' % (username, email))
                print(e)
                return HttpResponse(u"发送邮件错误!\n注册失败", status=500)

            new_user = form.save()
            user = auth.authenticate(username=email, password=password2)
            auth.login(request, user)

        else:
            # 如果表单不正确,保存错误到errors列表中
            for k, v in form.errors.items():
                # v.as_text() 详见django.forms.util.ErrorList 中
                errors.append(v.as_text())

        mydict = {"errors": errors}

        return HttpResponse(json.dumps(mydict), content_type="application/json")

    def changepassword(self, request):
        if not request.user.is_authenticated():
            logger.error(u'[UserControl]用户未登录')
            raise PermissionDenied

        form = PasswordChangeForm(request.user, request.POST)

        errors = []
        # 验证表单是否正确
        if form.is_valid():
            user = form.save()
            auth.logout(request)
        else:
            # 如果表单不正确,保存错误到errors列表中
            for k, v in form.errors.items():
                # v.as_text() 详见django.forms.util.ErrorList 中
                errors.append(v.as_text())

        mydict = {"errors": errors}
        return HttpResponse(json.dumps(mydict), content_type="application/json")

    def forgetpassword(self, request):
        username = self.request.POST.get("username", "")
        email = self.request.POST.get("email", "")

        form = VmaigPasswordRestForm(request.POST)

        errors = []

        # 验证表单是否正确
        if form.is_valid():
            token_generator = default_token_generator
            from_email = None
            opts = {
                'token_generator': token_generator,
                'from_email': from_email,
                'request': request,
            }
            user = form.save(**opts)

        else:
            # 如果表单不正确,保存错误到errors列表中
            for k, v in form.errors.items():
                # v.as_text() 详见django.forms.util.ErrorList 中
                errors.append(v.as_text())

        mydict = {"errors": errors}
        return HttpResponse(json.dumps(mydict), content_type="application/json")

    def resetpassword(self, request):
        uidb64 = self.request.POST.get("uidb64", "")
        token = self.request.POST.get("token", "")
        password1 = self.request.POST.get("password1", "")
        password2 = self.request.POST.get("password2", "")

        try:
            uid = urlsafe_base64_decode(uidb64)
            user = MyUser._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None

        token_generator = default_token_generator

        if user is not None and token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.POST)
            errors = []
            if form.is_valid():
                user = form.save()
            else:
                # 如果表单不正确,保存错误到errors列表中
                for k, v in form.errors.items():
                    # v.as_text() 详见django.forms.util.ErrorList 中
                    errors.append(v.as_text())

            mydict = {"errors": errors}
            return HttpResponse(json.dumps(mydict), content_type="application/json")
        else:
            logger.error(u'[UserControl]用户重置密码连接错误:[%s]/[%s]' % (uidb64, token))
            return HttpResponse("密码重设失败!\n密码重置链接无效，可能是因为它已使用。可以请求一次新的密码重置.", status=403)


def list_users(request):
    return render(request, 'user_list.html')


def get_users(request):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    try:
        users = MyUser.objects.filter(username__icontains=request.GET['search'])
    except:
        users = MyUser.objects
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = users.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for user in users.all().order_by(sort)[offset:offset + limit]:
        recode = {'username': user.username, 'pk': user.pk,
                  'email': user.email, 'id_num': user.id_num, 'group': user.groups.all()[0].name, 'id': user.pk}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


def create_users(request):
    stu_detail = request.POST['stu_detail']
    try:
        id_num, username = stu_detail.split()[0], stu_detail.split()[1]
    except:
        return HttpResponse(json.dumps({'result': 0, 'message': '您提供的注册信息不足'}))
    try:
        user = MyUser.objects.get(id_num=id_num)
        return HttpResponse(json.dumps({'result': 0, 'message': '该用户名已注册'}))
    except:
        try:
            user = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
            user.set_password(id_num)
            user.save()
            user.groups.add(Group.objects.get(name='学生'))
            return HttpResponse(json.dumps({'result': 0, 'count': 1}))
        except:
            return HttpResponse(json.dumps({'result': 0, 'message': '注册时出现问题'}))


def update_user(request, pk):
    user = MyUser.objects.get(pk=pk)
    if request.method == 'POST':
        group = Group.objects.get(pk=request.POST['group_id'])
        user.groups.clear()
        user.groups.add(group)
        return redirect(reverse('user_list'))
    current_group_id = user.groups.all()[0].pk
    groups = Group.objects.all()
    return render(request, 'update_user.html',
                  context={'user': user, 'groups': groups, 'current_group_id': current_group_id})

