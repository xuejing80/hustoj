# encoding: utf-8
import json
import time
import _thread
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from auth_system.models import MyUser
from judge.models import ClassName, Problem, ChoiceProblem, Solution, SourceCode, SourceCodeUser, KnowledgePoint1, \
    KnowledgePoint2, Compileinfo
from judge.views import get_testCases
from work.models import HomeWork, HomeworkAnswer, BanJi, MyHomework, TempHomeworkAnswer
from django.contrib.auth.decorators import permission_required, login_required

"""
有关hustoj的一些记录
solution.result的意义：
 OJ_WT0 0  Pending // 正等待...
 OJ_WT1 1  Pending_Rejudging
 OJ_CI 2   Compiling
 OJ_RI 3   Running_Judging
 OJ_AC 4   Accepted
 OJ_PE 5   Presentation Error
 OJ_WA 6   Wrong Answer
 OJ_ML 8   Memory Limit Exceeded
 OJ_OL 9   Output Limit Exceeded
 OJ_RE 10  Runtime Error
 OJ_CE 11  Compilation Error
 OJ_CO 12  Compile_OK

"""


@permission_required('work.add_homework')
def add_homework(request):
    """
    新建作业
    :param request: 请求
    :return: post时返回新建题目的详细页面，get时返回新建题目页面
    """
    if request.method == 'POST':
        homework = HomeWork(name=request.POST['name'],
                            choice_problem_ids=request.POST['choice-problem-ids'],
                            problem_ids=request.POST['problem-ids'],
                            problem_info=request.POST['problem-info'],
                            choice_problem_info=request.POST['choice-problem-info'],
                            courser=ClassName.objects.get(pk=request.POST['classname']),
                            start_time=request.POST['start_time'],
                            end_time=request.POST['end_time'],
                            allowed_languages=','.join(request.POST.getlist('languages')),
                            total_score=request.POST['total_score'],
                            creater=request.user)
        homework.save()
        return redirect(reverse("homework_detail", args=[homework.pk]))
    classnames = ClassName.objects.all()
    return render(request, 'homework_add.html', context={'classnames': classnames, 'title': '新建作业'})


@permission_required('work.change_homework')
def get_json_work(request):
    """
    获取作业列表数据
    :param request: 请求
    :return: 包含作业列表的json
    """
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    if request.GET['my'] == 'true':
        homeworks = MyHomework.objects.filter(creater=request.user).all()
    else:
        homeworks = HomeWork.objects.all()
    if classname != '0':
        homeworks = homeworks.filter(courser__id=classname)
    try:
        homeworks = homeworks.filter(name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = '-start_time'
    json_data['total'] = homeworks.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework in homeworks.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': homework.name, 'pk': homework.pk,
                  'courser': homework.courser.name, 'id': homework.pk,
                  'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S')}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


@permission_required('work.add_homework')
def list_homework(request):
    """
    列出所有作业
    :param request:
    :return:含有班级列表的页面
    """
    context = {'classnames': ClassName.objects.all(), 'position': 'public_work_manage'}
    return render(request, 'homework_list.html', context=context)


# 删除作业
@permission_required('work.delete_homework')
def del_homework(request):
    """
    删除作业
    :param request:
    :return:
    """
    if request.method == 'POST':
        my = request.POST['my']
        ids = request.POST.getlist('ids[]')
        if my == 'true':  # 判断是私有作业还是公共作业
            objects = MyHomework.objects
        else:
            objects = HomeWork.objects
        try:
            for pk in ids:
                objects.get(pk=pk).delete()
        except ObjectDoesNotExist:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 显示作业详细
@permission_required('work.change_homework')
def show_homework(request, pk):
    """
    显示作业详细页面
    :param request:
    :param pk: 作业主键值
    :return: 作业的详细介绍页面
    """
    homework = get_object_or_404(HomeWork, pk=pk)
    context = {'id': homework.id, 'name': homework.name, 'courser': homework.courser.name,
               'start_time': homework.start_time, 'end_time': homework.end_time,
               'title': '公开作业“' + homework.name + '”的详细'}
    return render(request, 'homework_detail.html', context=context)


# 显示我的作业详细
@permission_required('work.change_homework')
def show_my_homework(request, pk):
    """
    显示我的作业详细
    :param request:请求
    :param pk:作业主键
    :return:作业的详细页面
    """
    homework = get_object_or_404(MyHomework, pk=pk)
    total_students_number = 0
    for banji in homework.banji.all():
        total_students_number += banji.students.count()  # 需要完成作业总人数
    context = {'id': homework.id, 'name': homework.name, 'courser': homework.courser.name,
               'start_time': homework.start_time, 'end_time': homework.end_time, 'banjis': homework.banji.all(),
               "finished_students_number": homework.finished_students.count(),
               'total_students_number': total_students_number, 'title': '我的私有作业“' + homework.name + '”的详细'}
    return render(request, 'my_homework_detail.html', context=context)


@permission_required('work.change_homework')
def ajax_for_homework_info(request):
    """
    请求作业信息
    :param request: 请求
    :return: 含有作业信息的json
    """
    homework_id = request.POST['homework_id']
    if request.POST['my'] == 'true':
        homework = MyHomework.objects.get(pk=homework_id)
    else:
        homework = HomeWork.objects.get(pk=homework_id)
    result = {'problem_info': json.loads(homework.problem_info),
              'choice_problem_info': json.loads(homework.choice_problem_info)}
    return JsonResponse(result)


@permission_required('work.change_homework')
def update_public_homework(request, pk):
    """
    更新公共作业
    :param request: 请求
    :param pk: 公共作业主键值
    :return: 被修改作业的详细页面
    """
    homework = get_object_or_404(HomeWork, pk=pk)
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.courser = ClassName.objects.get(pk=request.POST['classname'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.problem_info = request.POST['problem-info']
        homework.total_score = request.POST['total_score']
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.save()
        return redirect(reverse("homework_detail", args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id, 'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改公开作业 "' + homework.name + '"'}
    return render(request, 'homework_add.html', context=context)


@permission_required('work.change_homework')
def update_my_homework(request, pk):
    """
    更新私有作业
    :param request: 请求
    :param pk: 私有作业主键
    :return: 私有作业详细页面
    """
    homework = get_object_or_404(MyHomework, pk=pk)
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.courser = ClassName.objects.get(pk=request.POST['classname'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.problem_info = request.POST['problem-info']
        homework.total_score = request.POST['total_score']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.allow_resubmit = True if request.POST['allow_resubmit'] == '1' else False
        homework.save()
        return redirect(reverse('my_homework_detail', args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id, 'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改我的作业"' + homework.name + '"',
                   'allow_resubmit': '1' if homework.allow_resubmit else '0'}
    return render(request, 'homework_add.html', context=context)  # 查看作业结果


@login_required()
def show_homework_result(request, id):
    """
    显示作业结果
    :param request: 请求
    :param id: 作业答案逐渐值
    :return: 作业结果详细页面
    """
    homework_answer = HomeworkAnswer.objects.get(pk=id)
    if request.user != homework_answer.creator and homework_answer.homework.creater != request.user and (
            not request.user.is_superuser):  # 检测用户是否有权查看
        return render(request, 'warning.html', context={
            'info': '您无权查看其他同学的作业结果'})
    if not homework_answer.judged:  # 如果作业还未批改完成
        return render(request, 'information.html', context={
            'info': '作业正在批改,请稍后刷新查看或到已完成作业列表中查看'})
    # 作业批改完成而且用户有权查看时
    wrong_id = homework_answer.wrong_choice_problems.split(',')  # todo 应该该讲两个字段合并
    wrong_info = homework_answer.wrong_choice_problems_info.split(',')
    homework = homework_answer.homework
    choice_problems = []
    problems = []
    for info in json.loads(homework.choice_problem_info):  # 载入作业的选择题信息，并进行遍历
        if str(info['id']) in wrong_id:  # 如果答案有错
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': False,
                 'info': wrong_info[wrong_id.index(str(info['id']))]})
        else:  # 如果答案正确
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': True})
    for solution in homework_answer.solution_set.all():  # 遍历homework_answer的所有solution
        problems.append({'code': SourceCode.objects.get(solution_id=solution.solution_id).source,
                         'title': Problem.objects.get(pk=solution.problem_id).title, 'result': solution.result})
    return render(request, 'homework_result.html',
                  context={'choice_problems': choice_problems, 'problem_score': homework_answer.problem_score,
                           'choice_problem_score': homework_answer.choice_problem_score,
                           'score': homework_answer.score, 'problems': problems,
                           'title': ' {}的"{}"详细'.format(homework_answer.creator.username, homework.name)})


def get_choice_score(homework_answer):
    """
    获取选择题成绩
    :param homework_answer: 需要获取成绩的作业答案
    :return: 选择题成绩
    """
    choice_problem_score = 0
    for info in json.loads(homework_answer.homework.choice_problem_info):  # 获取并遍历所属作业的选择题信息
        if str(info['id']) not in homework_answer.wrong_choice_problems.split(','):  # 如果答案正确
            choice_problem_score += int(info['total_score'])
    return choice_problem_score


# 显示作业并处理作业答案
@login_required()
def do_homework(request, homework_id):
    """
    做题
    :param request: 请求
    :param homework_id:作业的id
    :return: 重定向
    """
    if request.method == 'POST':  # 当提交作业时
        wrong_ids, wrong_info = '', ''
        homework = MyHomework.objects.get(pk=homework_id)
        if time.mktime(homework.end_time.timetuple()) < time.time():
            return render(request, 'warning.html', context={'info': '提交时间晚于作业的截止时间，提交失败'})
        if not homework.allow_resubmit:
            if request.user in homework.finished_students.all():  # 防止重复提交
                return render(request, 'warning.html', context={'info': '您已提交过此题目，请勿重复提交'})
            else:
                homework.finished_students.add(request.user)
                try:
                    HomeworkAnswer.objects.get(homework=homework, creator=request.user)
                    return render(request, 'warning.html', context={'info': '您已提交过此题目，请勿重复提交'})
                except ObjectDoesNotExist:
                    pass
            homeworkAnswer = HomeworkAnswer(creator=request.user, homework=homework)
        else:
            try:
                homeworkAnswer = HomeworkAnswer.objects.get(creator=request.user, homework=homework)
                for solution in homeworkAnswer.solution_set.all():
                    SourceCode.objects.get(solution_id=solution.solution_id).delete()
                    solution.delete()
                homeworkAnswer.judged = False
            except ObjectDoesNotExist:
                homework.finished_students.add(request.user)
                homeworkAnswer = HomeworkAnswer(creator=request.user, homework=homework)
        homeworkAnswer.save()

        # 判断选择题，保存错误选择题到目录
        for id in homework.choice_problem_ids.split(','):
            if id and request.POST.get('selection-' + id, 'x') != ChoiceProblem.objects.get(pk=id).right_answer:
                wrong_ids += id + ','  # 保存错误题目id
                wrong_info += request.POST.get('selection-' + id, '未回答') + ','  # 保存其回答记录

        # 创建编程题的solution，等待oj后台轮询判题
        for k, v in request.POST.items():
            if k.startswith('source'):
                code = v if v else  "未回答"
                solution = Solution(problem_id=k[7:], user_id=request.user.username,
                                    language=request.POST['language-' + k[7:]], ip=request.META['REMOTE_ADDR'],
                                    code_length=len(v))
                solution.save()
                homeworkAnswer.solution_set.add(solution)
                source_code = SourceCode(solution_id=solution.solution_id, source=code)
                source_code.save()
        homeworkAnswer.wrong_choice_problems = wrong_ids
        homeworkAnswer.wrong_choice_problems_info = wrong_info
        homeworkAnswer.save()

        # 开启判题进程，保存编程题目分数
        _thread.start_new_thread(judge_homework, (homeworkAnswer,))
        try:  # 如果有暂存的该作业答案，删除掉
            TempHomeworkAnswer.objects.get(creator=request.user, homework=homework).delete()
        except ObjectDoesNotExist:
            pass
        return redirect(reverse('show_homework_result', args=[homeworkAnswer.id]))
    else:  # 当正常访问时
        homeowork = MyHomework.objects.get(pk=homework_id)
        choice_problems = []
        for id in homeowork.choice_problem_ids.split(','):
            if id:
                choice_problems.append({'detail': ChoiceProblem.objects.get(pk=id),
                                        'score': json.loads(homeowork.choice_problem_info)[0]['total_score']})
        problems = []
        for id in homeowork.problem_ids.split(','):
            if id:
                problems.append(Problem.objects.get(pk=id))
        return render(request, 'do_homework.html',
                      context={'homework': homeowork, 'problems': problems, 'choice_problems': choice_problems,
                               'title': homeowork.name})


@permission_required('work.add_banji')
def add_banji(request):
    """
    新建班级
    :param request: 请求
    :return: POST则返回班级的详细页面，GET则返回班级详细页面
    """
    if request.method == 'POST':
        banji = BanJi(name=request.POST['name'], start_time=request.POST['start_time'], teacher=request.user,
                      end_time=request.POST['end_time'],
                      courser=ClassName.objects.get(pk=request.POST['classname']))
        banji.save()
        banji.students.add(request.user)
        banji.save()
        return redirect(reverse('banji_detail', args=(banji.id,)))
    return render(request, 'banji_add.html', context={'classnames': ClassName.objects.all(), 'title': "新建班级"})


@permission_required('work.add_classname')
def add_courser(request):
    """
    新建课程
    :param request: 请求
    :return: 成功返回1
    """
    courser = ClassName(name=request.POST['name'])
    courser.save()
    return HttpResponse(1)


@permission_required('work.add_banji')
def list_banji(request):
    """
    列出班级
    :param request: 请求
    :return: 班级列表页面
    """
    classnames = ClassName.objects.all()
    context = {'classnames': classnames, 'title': '班级列表', 'position': 'banji_manage'}
    return render(request, 'banji_list.html', context=context)


@permission_required('work.add_banji')
def get_banji_list(request):
    """
    处理获取班级列表信息的ajax请求
    :param request: 请求
    :return: 含有班级列表信息的json
    """
    json_data = {}
    recodes = []
    kwargs = {}
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    classname = request.GET['classname']
    if request.GET['my'] == 'true' and not request.user.is_superuser:
        kwargs['teacher'] = request.user
    if classname != '0':
        kwargs['courser__id'] = classname
    if 'search' in request.GET:
        kwargs['name__icontains'] = request.GET['search']
    banjis = BanJi.objects.filter(**kwargs)  # 合并多次筛选以提高数据库效率
    try:  # 对数据按照指定方式排序
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = banjis.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for banji in banjis.all().order_by(sort)[offset:offset + limit]:
        recode = {'name': banji.name, 'pk': banji.pk,
                  'courser': banji.courser.name, 'id': banji.pk, 'teacher': banji.teacher.username,
                  'start_time': banji.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'end_time': banji.end_time.strftime('%Y-%m-%d %H:%M:%S')}
        recodes.append(recode)
    json_data['rows'] = recodes
    return JsonResponse(json_data)


# 删除班级
@permission_required('work.delete_banji')
def del_banji(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                BanJi.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 更新班级信息
@permission_required('work.change_banji')
def update_banji(request, id):
    banji = get_object_or_404(BanJi, pk=id)
    if request.method == 'POST':
        banji.name = request.POST['name']
        banji.start_time = request.POST['start_time']
        banji.end_time = request.POST['end_time']
        banji.courser = ClassName.objects.get(pk=request.POST['classname'])
        banji.save()
        return redirect(reverse('banji_detail', args=(banji.id,)))
    else:
        return render(request, 'banji_add.html',
                      context={'name': banji.name, 'start_time': banji.start_time, 'end_time': banji.end_time,
                               'courser_id': banji.courser.pk, 'classnames': ClassName.objects.all(),
                               'title': '修改班级信息'})


# 复制公共作业到私有作业
@permission_required('work.add_myhomework')
def copy_to_my_homework(request):
    ids = request.POST.getlist('ids[]')
    try:
        for pk in ids:
            old_homework = HomeWork.objects.get(pk=pk)
            homework = MyHomework(name=old_homework.name, courser=old_homework.courser, creater=request.user,
                                  start_time=old_homework.start_time, end_time=old_homework.end_time,
                                  problem_ids=old_homework.problem_ids,
                                  choice_problem_ids=old_homework.choice_problem_ids,
                                  problem_info=old_homework.problem_info,
                                  choice_problem_info=old_homework.choice_problem_info,
                                  allowed_languages=old_homework.allowed_languages,
                                  total_score=old_homework.total_score)  # todo 有更好的方法
            homework.save()
    except:
        return HttpResponse(0)
    return HttpResponse(1)


@permission_required('work.add_homework')
def list_my_homework(request):
    classnames = ClassName.objects.all()
    context = {'classnames': classnames, 'title': '我的私有作业列表', 'position': 'private_work_manage'}
    return render(request, 'my_homework_list.html', context=context)


@permission_required('work.add_banji')
def show_banji(request, pk):
    banji = BanJi.objects.get(pk=pk)
    context = {'id': banji.id, 'name': banji.name, 'courser': banji.courser.name, 'start_time': banji.start_time,
               'end_time': banji.end_time, 'teacher': banji.teacher.username, 'students': banji.students.all(),
               'title': '班级"' + banji.name + '"的信息'}
    return render(request, 'banji_detail.html', context=context)


@permission_required('work.change_banji')
def add_students(request, pk):
    return render(request, 'add_students.html', context={'id': pk, 'title': '添加学生到班级'})


@permission_required('work.change_banji')
def ajax_add_students(request):
    stu_detail = request.POST['stu_detail']
    banji_id = request.POST['banji_id']
    if len(stu_detail.split()) > 1:
        id_num, username = stu_detail.split()[0], stu_detail.split()[1]
        try:
            student = MyUser.objects.get(id_num=id_num)
        except:
            student = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
            student.set_password(id_num)
            student.save()
            student.groups.add(Group.objects.get(name='学生'))
    else:
        try:
            student = MyUser.objects.get(id_num=stu_detail)
        except:
            return HttpResponse(json.dumps({'result': 0, 'message': '该学号未注册，且您未提供注册信息'}))
    banji = BanJi.objects.get(pk=banji_id)
    banji.students.add(student)
    return HttpResponse(json.dumps({'result': 0, 'count': 1}))


@permission_required('work.add_homework')
def assign_homework(request):
    homework_id = request.POST['homework_id']
    banji_id = request.POST['id']
    try:
        homework = MyHomework.objects.get(pk=homework_id)
        banji = BanJi.objects.get(pk=banji_id)
        banji.myhomework_set.add(homework)
        return HttpResponse(json.dumps({'result': 0, 'count': 1}))
    except:
        return HttpResponse(json.dumps({'result': 0, 'message': '出错了'}))


# 显示我的待做作业
@login_required()
def list_do_homework(request):
    banjis = BanJi.objects.filter(students=request.user).all()
    return render(request, 'do_homework_list.html',
                  context={'banjis': banjis, 'title': '尚未完成的作业', 'position': 'unfinished'})


# 获取待做作业列表
@login_required()
def get_my_homework_todo(request):
    user = request.user
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    banji = request.GET['banji']
    count = 0
    homeworks = MyHomework.objects.filter(banji__students=user)
    if banji != '0':
        homeworks = homeworks.filter(banji__id=banji)
    try:
        homeworks = homeworks.filter(name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework in homeworks.all().order_by(sort):
        if (request.user not in homework.finished_students.all()) and (homework.start_time < timezone.now() < homework.end_time):
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S')}
            recodes.append(recode)
            count += 1
    json_data['rows'] = recodes[offset:offset + limit]
    json_data['total'] = count
    json_data['xxx'] = homeworks.count()
    return JsonResponse(json_data)


def get_problem_score(homework_answer, judged_score=0):
    """
    获取某次作业的分数
    :param judged_score: 经过之前测试运行得到的分数
    :param homework_answer: 已提交的作业
    :return: 作业的编程题部分分数
    """
    score = judged_score
    homework = homework_answer.homework
    solutions = homework_answer.solution_set
    problem_info = []
    for info in json.loads(homework.problem_info):
        try:
            solution = solutions.get(problem_id=info['id'])  # 获取题目
            for case in info['testcases']:  # 获取题目的测试分数
                if solution.result == 11:  # 如果题目出现编译错误，直接判断为0分，不再继续判断
                    break
                if json.loads(solution.oi_info)[str(case['desc']) + '.in']['result'] == 4:  # 参照测试点，依次加测试点分数
                    score += int(case['score'])
        except Exception as e:
            print("error on get problem score！homework_id: %d ,error : %s args: %s" % (
                homework.pk, e, e.args.__str__()))
    return score


@login_required()
def list_finished_homework(request):
    return render(request, 'finidshed_homework_list.html',
                  context={'classnames': ClassName.objects.all(), 'position': 'finished', 'title': '已经完成的作业'})


@login_required()
def get_finished_homework(request):
    """
    获取用户已经完成的作业记录
    :param request: 请求
    :return: 含有用户已完成作业的json
    """
    json_data = {}
    recodes = []
    user = request.user
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    homework_answers = HomeworkAnswer.objects.filter(creator=user)
    if request.GET['classname'] != '0':
        homework_answers = homework_answers.filter(homework__courser=HomeWork.objects.get(pk=request.GET['classname']))
    try:
        homework_answers = homework_answers.filter(homework__name__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    homework_answers = homework_answers.filter()
    json_data['total'] = homework_answers.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework_answer in homework_answers.all().order_by(sort)[offset:offset + limit]:
        score = '{}'.format(homework_answer.score) if homework_answer.judged else '<i class="fa fa-spinner fa-spin fa-fw"></i> 作业还在判分中'
        recode = {'name': homework_answer.homework.name,
                  'create_time': homework_answer.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'id': homework_answer.pk,
                  'teacher': 'dd',
                  'score': score,
                  'allow_resubmit': homework_answer.homework.allow_resubmit,
                  'homework_id': homework_answer.homework.id
                  }
        recodes.append(recode)
    json_data['rows'] = recodes
    return JsonResponse(json_data)


@permission_required('work.add_homework')
def get_finished_students(request):
    json_data = {}
    recodes = []
    homework_id = request.GET['homework_id']
    homework = MyHomework.objects.get(pk=homework_id)
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    homework_answers = homework.homeworkanswer_set
    if request.GET['banji_id'] != '0':
        homework_answers = homework_answers.filter(
            creator__banJi_students=BanJi.objects.get(id=request.GET['banji_id']))
    try:
        homework_answers = homework_answers.filter(creator__id_num__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    homework_answers = homework_answers.filter()
    json_data['total'] = homework_answers.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for homework_answer in homework_answers.all().order_by(sort)[offset:offset + limit]:
        score = '{}'.format(homework_answer.score) if homework_answer.judged else '<i class="fa fa-spinner fa-spin fa-fw"></i> 作业还在判分中'
        recode = {'id_num': homework_answer.creator.id_num,
                  'username': homework_answer.creator.username,
                  'create_time': homework_answer.create_time.strftime('%Y-%m-%d %H:%M:%S'), 'id': homework_answer.id,
                  'teacher': 'dd',
                  'score': score
                  }
        recodes.append(recode)
    json_data['rows'] = recodes
    return JsonResponse(json_data)


@permission_required('work.add_classname')
def list_coursers(request):
    """
    列出课程
    """
    coursers = ClassName.objects.all()
    return render(request, 'courser_list.html', {'coursers': coursers, 'title': '课程列表', 'position': 'courser_manage'})


@permission_required('work.add_knowledgepoint1')
def list_kp1s(request, id):
    courser = ClassName.objects.get(id=id)
    kp1s = KnowledgePoint1.objects.filter(classname=courser)
    return render(request, 'kp1_list.html', {'kp1s': kp1s, 'title': '查看课程“%s”的一级知识点' % courser.name, 'id': id})


@permission_required('work.add_knowledgepoint2')
def list_kp2s(request, id):
    kp1 = KnowledgePoint1.objects.get(id=id)
    kp2s = KnowledgePoint2.objects.filter(upperPoint=kp1)
    return render(request, 'kp2s_list.html', context={'kp2s': kp2s, 'id': id, 'title': '查看一级知识点"%s”下的二级知识点' % kp1.name})


@permission_required('work.delete_classname')
def delete_courser(request):
    try:
        ClassName.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.delete_knowledgepoint1')
def delete_kp1(request):
    try:
        KnowledgePoint1.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.delete_knowledgepoint2')
def delete_kp2(request):
    try:
        KnowledgePoint2.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('work.add_knowledgepoint1')
def add_kp1(request):
    kp1 = KnowledgePoint1(name=request.POST['name'], classname_id=request.POST['id'])
    kp1.save()
    return HttpResponse(1)


@permission_required('work.add_knowledgepoint2')
def add_kp2(request):
    kp2 = KnowledgePoint2(name=request.POST['name'], upperPoint_id=request.POST['id'])
    kp2.save()
    return HttpResponse(1)


def judge_homework(homework_answer):
    # todo 效率很低，有待改进
    """
    评判作业，修改作业的成绩信息
    :param homework_answer:提交的作业
    :return:None
    """
    for i in range(2000):
        if i == 1000:
            for solution in homework_answer.solution_set.all():
                if solution.result in [0, 1, 2, 3]:
                    solution.result = 0
                    solution.save()
        for solution in homework_answer.solution_set.all():  # 遍历作业的solution集合
            if solution.result in [0, 1, 2, 3]:  # 当存在solution还在判断中时，重新进行遍历
                time.sleep(0.1)
                break  # 跳出对solution的遍历，重新从头开始遍历
            else:
                continue
        else:  # 如果全部solution都已判断结束
            choice_problem_score = get_choice_score(homework_answer)  # 获取选择题分数
            homework_answer.choice_problem_score = choice_problem_score
            problem_score = get_problem_score(homework_answer)  # 获取编程题分数
            homework_answer.problem_score = problem_score
            homework_answer.score = choice_problem_score + problem_score  # 计算总分
            homework_answer.judged = True  # 修改判题标记为已经判过
            homework_answer.save()  # 保存
            break  # 跳出循环


@permission_required('work.add_myhomework')
def add_myhomework(request):
    """
    新建私有作业
    :param request:请求
    :return: 如果为GET请求，返回新建作业页面，如果为POST，返回到新建的题目的
    """
    if request.method == 'POST':
        allow_resubmit = True if request.POST['allow_resubmit'] == "1" else False
        homework = MyHomework(name=request.POST['name'],
                              choice_problem_ids=request.POST['choice-problem-ids'],
                              problem_ids=request.POST['problem-ids'],
                              problem_info=request.POST['problem-info'],
                              choice_problem_info=request.POST['choice-problem-info'],
                              courser=ClassName.objects.get(pk=request.POST['classname']),
                              start_time=request.POST['start_time'],
                              end_time=request.POST['end_time'],
                              allowed_languages=','.join(request.POST.getlist('languages')),
                              total_score=request.POST['total_score'],
                              creater=request.user,
                              allow_resubmit=allow_resubmit)
        homework.save()
        return redirect(reverse("my_homework_detail", args=[homework.pk]))
    classnames = ClassName.objects.all()
    return render(request, 'homework_add.html', context={'classnames': classnames, 'title': '新建私有作业'})


def test_run(request):
    """
    提交作业前提供的测试运行函数
    :param request: 请求
    :return: 包含运行结果的json数据
    """
    if request.POST['type'] == 'upload':  # 当上传代码时
        try:
            solution = Solution(problem_id=request.POST['problem_id'], user_id=request.user.username,
                                language=request.POST['language'], ip=request.META['REMOTE_ADDR'],
                                code_length=len(request.POST['code']))  # 创建判题的solutioon
            solution.save()
            source_code = SourceCode(solution_id=solution.solution_id, source=request.POST['code'])
            source_code.save()
            return HttpResponse(
                json.dumps({'result': 1, 'solution_id': solution.solution_id}))  # 创建成功，返回solutioon_id
        except Exception as e:
            return HttpResponse(json.dumps({'result': 0, 'info': '出现了问题' + e.__str__(), 'score': 0}))  # 创建失败，返回错误信息
    if request.POST['type'] == 'score':  # 当获取结果时

        solution = Solution.objects.get(solution_id=request.POST['solution_id'])  # 获取solution
        homework = MyHomework.objects.get(id=request.POST['homework_id'])
        if solution.result in [0, 1, 2, 3]:  # 当题目还在判断中时
            return HttpResponse(json.dumps({'status': 0, 'info': '题目正在判断中', 'score': 0}))
        if solution.result == 11:  # 当出现编译错误时
            SourceCode.objects.get(solution_id=solution.solution_id).delete()
            solution.delete()
            try:
                compile_info = Compileinfo.objects.get(
                    solution_id=request.POST['solution_id']).error
            except:
                compile_info = ''
            return JsonResponse(
                {'status': 1, 'result': 0, 'info': {'info': '编译出错:\n' + compile_info, 'score': 0}})
        else:  # 当成功编译时
            result = 2  # 2代表通过全部测试用例
            right_num = wrong_num = 0  # 通过的测试点数量和未通过的测试点数量
            problem = Problem.objects.get(pk=request.POST['problem_id'])
            cases = get_testCases(problem)
            score = 0
            for info in json.loads(homework.problem_info):
                if info['pk'] == solution.problem_id:
                    for case in info['testcases']:  # 获取题目的测试分数
                        if json.loads(solution.oi_info)[str(case['desc']) + '.in']['result'] == 4:  # 参照测试点，依次加测试点分数
                            score += int(case['score'])
                            right_num += 1
                        else:
                            wrong_num += 1
                            result = 1
            SourceCode.objects.get(solution_id=solution.solution_id).delete()
            solution.delete()
            return JsonResponse({'status': 1, 'result': result,
                                 'info': {'total_cases': len(cases), 'right_num': right_num,
                                          'wrong_num': wrong_num, 'score': score}})


@login_required()
def delete_homeworkanswer(request, id):
    """
    去除指定人的作业完成状态
    :param request: 请求
    :param id: 作业回答id
    :return: 重定向到作业详细界面
    """
    homeworkanswer = HomeworkAnswer.objects.get(pk=id)
    homwork_id = homeworkanswer.homework_id
    if homeworkanswer.homework.creater != request.user and not request.user.is_superuser:
        return JsonResponse({'error': 'you are not admin'})
    homeworkanswer.homework.finished_students.remove(homeworkanswer.creator)
    for solution in homeworkanswer.solution_set.all():
        SourceCode.objects.get(solution_id=solution.solution_id).delete()
        solution.delete()
    homeworkanswer.delete()
    return redirect(reverse('my_homework_detail', kwargs={'pk': homwork_id}))


@permission_required('work.change_homework')
def rejudge_homework(request, id):
    """
    对作业进行重新判分
    :param request:请求
    :param id:题目id
    :return:
    """
    homework_answer = HomeworkAnswer.objects.get(pk=id)
    for i in homework_answer.solution_set.all():
        i.result = 0
        i.save()
    homework_answer.judged = False
    _thread.start_new_thread(judge_homework, (homework_answer,))
    homework_answer.homework.finished_students.add(homework_answer.creator)
    return redirect(reverse('my_homework_detail', args=(homework_answer.homework.id,)))


def save_homework_temp(request):
    """
    暂存作业
    :param request: 请求
    :return: 重定向到作业列表
    """
    data = request.POST.dict()
    homework = MyHomework.objects.get(id=data['homework_id'])
    del data['csrfmiddlewaretoken']  # 去除表单中的scrf项
    del data['homework_id']  # 去除表单中的homework_id项
    TempHomeworkAnswer.objects.update_or_create(homework=homework, creator=request.user,
                                                defaults={'data': json.dumps(data)})
    return redirect(reverse('list_do_homework'))


def init_homework_data(request):
    try:
        temp = TempHomeworkAnswer.objects.get(homework_id=request.POST['homework_id'], creator=request.user)
        return JsonResponse({'result': 1, 'data': json.loads(temp.data)})
    except Exception as e:
        return JsonResponse({'result': -1})


def file_download(request):
    return render(request, 'file_download.html', context={'title': '教学资源下载', 'position': 'source'})

# def list_depl_homeworks(request):
#     return render(request,'depl_homework_list.html')
#
# def get_depl_homeworks(request):
#     json_data = {}
#     recodes = []
#     offset = int(request.GET['offset'])
#     limit = int(request.GET['limit'])
#     homeworks = MyHomework.objects.filter(creater=request.user).filter(banjis)
#     try:
#         homeworks = homeworks.filter(name__icontains=request.GET['search'])
#     except:
#         pass
#     try:
#         sort = request.GET['sort']
#     except MultiValueDictKeyError:
#         sort = 'pk'
#     json_data['total'] = homeworks.count()
#     if request.GET['order'] == 'desc':
#         sort = '-' + sort
#     for homework in homeworks.all().order_by(sort)[offset:offset + limit]:
#         recode = {'name': homework.name, 'pk': homework.pk,
#                   'courser': homework.courser.name, 'id': homework.pk,
#                   'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
#                   'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S')}
#         recodes.append(recode)
#     json_data['rows'] = recodes
#     return HttpResponse(json.dumps(json_data))
