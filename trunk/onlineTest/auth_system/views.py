# coding:utf-8
from django.contrib.auth.models import Group, AbstractUser
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import View
from django.core.mail import send_mail
from django.core.exceptions import PermissionDenied
from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import ValidationError
from django.db.models import Count, Sum
from .forms import VmaigUserCreationForm, VmaigPasswordRestForm, PasswordChangeForm, EmailChangeForm, SetPasswordForm
from .models import MyUser
from census.views import Nums, Dates, Record
from judge.models import ChoiceProblem, DuchengProblem, Problem, ClassName
from work.models import BanJi, MyHomework
import json, base64
from django.http import HttpResponse, HttpResponseRedirect, Http404

import re,os
from django.db.models import Q
from django.conf import settings
# logger
import logging
logger = logging.getLogger('django')
logger_request = logging.getLogger('django.request')

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
        elif slug == "resetpassword_mail":
            return self.resetpassword_mail(request)

        raise PermissionDenied

    def get(self, request, *args, **kwargs):
        # 如果是get请求直接返回404页面
        raise Http404

    def login(self, request):
        errors = []
        error_code = 0
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        next = request.POST.get("next", "")
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
            if user.id_num==password:
                errors.append("您的账号为初始账号，请完善账号信息！")
                error_code = 2
                auth.login(request, user)
            else:
                auth.login(request, user)
        else:
            errors.append("密码或者用户名不正确")
            error_code = 1

        mydict = {"errors": errors,"code": error_code}
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
            title = u"欢迎注册%s！" % (settings.SITE_NAME)
            message = u"你好！ %s ,感谢注册%s ！\n\n" % (username,settings.SITE_NAME) + \
                      u"请牢记以下信息：\n" + \
                      u"用户名：%s \n" % id_num + \
                      u"昵称：%s" % username + "\n" + \
                      u"邮箱：%s" % email + "\n" + \
                      u"网站：http://%s" % domain + "/\n\n"
            from_email = settings.EMAIL_HOST_USER
            try:
                os.system("echo '%s' | mail -s %s %s -aFrom:%s\<%s\>" % (message,title,email,settings.ADMINS[0][0],settings.ADMINS[0][1]))
                #send_mail(title, message, from_email, [email])
            except Exception as e:
                logger.error(u'[UserControl]用户注册邮件发送失败:[%s]/[%s](%s)' % (username, email, repr(e)))
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

    #@login_required()
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

    def resetpassword_mail(self, request):
        uidb64 = self.request.POST.get("uidb64", "")
        umailb64 = self.request.POST.get("umailb64", "")
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
            errors = []
            umail = urlsafe_base64_decode(umailb64)
            if user.email != umail:
                user.email = umail
            form = SetPasswordForm(user, request.POST)
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
            return HttpResponse("密码重置链接无效，可能是因为它已使用，您可以重新请求一次新的密码重置。", status=403)

@login_required()
def change_email(request):
    if request.method == 'POST':
        useOldEmail = request.POST["use_old_email"]
        form = EmailChangeForm(request.POST,instance=request.user)
        errors = []
        email = None
        if useOldEmail=="True":
            email = request.user.email
        elif form.is_valid():
            email = form.cleaned_data['email']
        if email!=None:
            user = request.user
            token_generator = default_token_generator
            from_email = settings.EMAIL_HOST_USER
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            uid = base64.urlsafe_b64encode(force_bytes(user.pk)).rstrip(b'\n=')
            umail = base64.urlsafe_b64encode(force_bytes(email)).rstrip(b'\n=')
            token = token_generator.make_token(user)
            protocol = 'http'
            uid = uid.decode("utf-8")
            umail = umail.decode("utf-8")
            title = "完善您的Email和密码信息"
            message = "你收到这封信是因为你请求完善在 %s 上的个人信息\n\n" % settings.SITE_NAME + \
                   "请访问下方的链接确认你的邮件地址并在页面中设置新的密码:\n\n" + \
                   protocol + '://' + domain + reverse('resetpassword_mail',args=(uid,umail,token)) + '  \n\n' + \
                   "感谢使用！\n\n"
            try:
                os.system("echo '%s' | mail -s %s %s -aFrom:%s\<%s\>" % (message,title,email,settings.ADMINS[0][0],settings.ADMINS[0][1]))
                #send_mail(title, message, from_email, [email])
            except Exception as e:
                logger.error(u'[UserControl]用户完善密码信息的邮件发送失败:[%s]' % (email))
                errors.append("很抱歉，邮件发送失败，请稍后重试！")
            return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")

        else:
            # 如果表单不正确,保存错误到errors列表中
            for k, v in form.errors.items():
                # v.as_text() 详见django.forms.util.ErrorList 中
                errors.append(v.as_text())
        mydict = {"errors": errors}
        return HttpResponse(json.dumps(mydict), content_type="application/json")
    else:
        form = EmailChangeForm()
        return render(request,'change_mail.html',{'form':form,'old_email':request.user.email})

@login_required()
def change_password(request):
    return render(request, 'demo/changepassword.html')

@permission_required('is_superuser')
def list_users(request):
    return render(request, 'user_list.html')

@permission_required('is_superuser')
def get_users(request):
    json_data = {}
    recodes = []

    if not request.user.is_superuser:
        raise PermissionDenied
    if request.GET.dict()=={}:
        return HttpResponse(json.dumps(json_data))

    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    usergroup = request.GET['usergroup']
    try:
        qset = Q()
        if 'search' in request.GET.dict().keys():
            qset = ( Q(username__icontains=request.GET['search']) | 
                     Q(email__icontains=request.GET['search']) |
                     Q(id_num__icontains=request.GET['search']) )
        if usergroup != '0':
            qset = qset & Q(groups=usergroup)
        users = MyUser.objects.filter(qset)
    except Exception as e:
        #import traceback
        #print(traceback.print_exc())
        users = MyUser.objects
    if 'sort' in request.GET.dict().keys():
        sort = request.GET['sort']
    else:
        sort = 'pk'
    json_data['total'] = users.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for user in users.all().order_by(sort)[offset:offset + limit]:
        recode = {'username': user.username, 'pk': user.pk,
                  'email': user.email, 'id_num': user.id_num, 
                  'group': user.groups.all()[0].name, 'school': user.school, 'id': user.pk}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))

@permission_required('is_superuser')
def create_users(request):
    if request.POST.dict()=={} and request.GET.dict()=={}:
        return render(request, 'add_users.html')    
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

@permission_required('is_superuser')
def update_user(request):
    try:
        pk = int(request.GET['pk'])
    except:
        raise Http404()
    
    user = get_object_or_404(MyUser, pk=pk)
    if request.method == 'POST':
        group = Group.objects.get(pk=request.POST['group_id'])
        if request.POST['password']!="":
            user.set_password(request.POST['password'])
        user.school = request.POST['school']
        user.school_short = request.POST['school_short']
        if user.isTeacher():   
            t = user.allow_num - user.create_num
            try:
                user.allow_num = int(request.POST['allow_num'])
            except:
                pass
            user.create_num = user.allow_num - t
            #print(user.create_num)
        user.groups.clear()
        user.groups.add(group)
        user.save()
        return redirect(reverse('user_list'))
    current_group_id = user.groups.all()[0].pk
    groups = Group.objects.all()
    return render(request, 'update_user.html',
                  context={'user': user, 'groups': groups, 'current_group_id': current_group_id})

@login_required()
def reset_user(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied

    user = MyUser.objects.get(pk=pk)
    user.set_password(user.id_num)
    user.save()
    return redirect(reverse('user_list'))

@csrf_exempt
def page_not_found(request):
    return render(request, 'warning.html', context={'info': '您访问的页面地址不存在！'})

@csrf_exempt
def page_error(request):
    return render(request, 'warning.html', context={'info': '服务器出错了，请联系管理员老师！(联系信息：'
             + settings.CONTACT_INFO + ')'})

@csrf_exempt
def permission_denied(request):
    return render(request, 'warning.html', context={'info': '您无权访问该页面！'})

@permission_required('is_superuser')
def dash_board(request):
    A = 'registered_users'
    B = 'choices'
    C = 'programms'
    D = 'fills'
    E = 'homework'
    Record()
    group = Group.objects.get(name='老师')
    teachers = group.user_set.all()
    context = {}
    context['javas'] = len(ChoiceProblem.objects.filter(classname=4))
    context['cpps'] = len(ChoiceProblem.objects.filter(classname=3))
    context['advances'] = len(ChoiceProblem.objects.filter(classname=1))
    context['dates'] = Dates()
    context['A'] = Nums(A)
    context['B'] = Nums(B)
    context['C'] = Nums(C)
    context['D'] = Nums(D)
    context['E'] = Nums(E)
    context['all_users_count'] = len(MyUser.objects.annotate(Count('Number_user')))
    result = MyUser.objects.aggregate(total=Count('school', distinct=True))
    context['school_count'] = result['total']
    context['all_teachers_count'] = len(teachers)
    context['my_homework'] = len(MyHomework.objects.all())
    context['choice_problem_count'] = len(ChoiceProblem.objects.annotate(Count('id')))
    context['pythons'] = context['choice_problem_count']-(context['javas']+context['cpps']+context['advances'])
    context['ducheng_problem_count'] = len(DuchengProblem.objects.annotate(Count('ducheng_id')))
    context['problem_count'] = len(Problem.objects.annotate(Count('problem_id')))
    context['banji_count'] = len(BanJi.objects.annotate(Count('banji')))
    # context['online_visitors'] = online_vistors
    return render(request, "dashboard.html", context)

@permission_required('is_superuser')
def monitor(request):
    try:
        user_id = int(request.GET['user_id'])
    except:
        raise Http404()

    user = MyUser._default_manager.get(id=user_id)
    if user is not None:
        pwd = user.password
        user.set_password('njupt123456')
        user.save()
        user = auth.authenticate(username=user.email, password='njupt123456')
        auth.logout(request)
        user.password = pwd
        user.save()
        auth.login(request, user)
    return HttpResponseRedirect(reverse('index'))
