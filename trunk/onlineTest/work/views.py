# encoding: utf-8
import os, shutil, zipfile, string, json, datetime, time, random
import _thread
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from django.core.urlresolvers import reverse
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from auth_system.models import MyUser
from judge.models import ClassName, Problem, ChoiceProblem, Solution, SourceCode, SourceCodeUser, KnowledgePoint1, \
    KnowledgePoint2, Compileinfo, DuchengProblem
from judge.views import get_testCases
from work.models import HomeWork, HomeworkAnswer, BanJi, MyHomework, TempHomeworkAnswer
from django.contrib.auth.decorators import permission_required, login_required
from django.conf import settings
from django.db.models import Q
from process.views import get_similarity, update_ansdb,get_similarity_v2
import logging

logger = logging.getLogger('django')
logger_request = logging.getLogger('django.request')

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
def global_settings(request):
    return{'SITE_NAME':settings.SITE_NAME}


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
                            ducheng_problem_ids=request.POST['ducheng-problem-ids'],
                            problem_ids=request.POST['problem-ids'],
                            tiankong_problem_ids=request.POST['tiankong-problem-ids'],
                            gaicuo_problem_ids=request.POST['gaicuo-problem-ids'],
                            problem_info=request.POST['problem-info'],
                            choice_problem_info=request.POST['choice-problem-info'],
                            ducheng_problem_info=request.POST['ducheng-problem-info'],
                            courser=ClassName.objects.get(pk=request.POST['course']),
                            start_time=request.POST['start_time'],
                            end_time=request.POST['end_time'],
                            allowed_languages=','.join(request.POST.getlist('languages')),
                            total_score=request.POST['total_score'],
                            creater=request.user,
                            work_kind=request.POST['work_kind'],
                            resubmit_number = request.POST['resubmit_number'],
                            allow_resubmit = True if request.POST['allow_resubmit'] == '1' else False,
                            allow_random = True if request.POST['allow_random'] == '1' else False,
                            allow_similarity = True if request.POST['allow_similarity'] == '1' else False,
                            show_answer = request.POST['show_answer'],
                            show_score = request.POST['show_score'])

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
                  'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'creator': homework.creater.username,
                  'isMine': request.user.is_admin or request.user==homework.creater,}
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
                homework = objects.get(pk=pk)
                if request.user == homework.creater or request.user.is_admin:
                    homework.delete()
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
               'start_time': homework.start_time, 'end_time': homework.end_time, 'work_kind': homework.work_kind,
               'title': '公共作业“' + homework.name + '”的详细'}
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
    homework_answers = homework.homeworkanswer_set
    banjiList = []
    for banji in homework.banji.all():
        if time.mktime(banji.start_time.timetuple()) < time.time() < time.mktime(banji.end_time.timetuple()):
            banjiList.append(banji.pk)
            total_students_number += banji.students.count()  # 需要完成作业总人数
    homework_answers = homework_answers.filter(
        creator__banJi_students__in=BanJi.objects.filter(id__in=banjiList))

    context = {'id': homework.id, 'name': homework.name, 'courser': homework.courser.name,
               'start_time': homework.start_time, 'end_time': homework.end_time, 'banjis': homework.banji.all(),
               "finished_students_number": homework_answers.count(), 'work_kind': homework.work_kind,
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
    result = []
    try:
        if request.POST['my'] == 'true':
            homework = MyHomework.objects.get(pk=homework_id)
        else:
            homework = HomeWork.objects.get(pk=homework_id)
        ducheng_problem_info = homework.ducheng_problem_info
        tiankong_info = homework.tiankong_problem_info

        if ducheng_problem_info is None:
            ducheng_problem_info = "[]"
        if tiankong_info is None:
            tiankong_info = "[]"
        gaicuo_info = homework.gaicuo_problem_info
        if gaicuo_info is None:
            gaicuo_info = "[]"
        result = {'problem_info': json.loads(homework.problem_info),
                  'choice_problem_info': json.loads(homework.choice_problem_info),
                  'ducheng_problem_info': json.loads(ducheng_problem_info),
                  'tiankong_problem_info': json.loads(tiankong_info),
                  'gaicuo_problem_info': json.loads(gaicuo_info)}
    except:
        logger_request.exception("执行动作：请求作业信息，用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict()))
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
    if request.user != homework.creater and request.user.is_admin!=True:
        raise PermissionDenied
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.ducheng_problem_ids = request.POST['ducheng-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.tiankong_problem_ids = request.POST['tiankong-problem-ids']
        homework.gaicuo_problem_ids = request.POST['gaicuo-problem-ids']
        homework.problem_info = request.POST['problem-info']
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.ducheng_problem_info = request.POST['ducheng-problem-info']
        homework.tiankong_problem_info = request.POST['tiankong-problem-info']
        homework.gaicuo_problem_info = request.POST['gaicuo-problem-info']
        homework.courser = ClassName.objects.get(pk=request.POST['course'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.total_score = request.POST['total_score']
        homework.work_kind = request.POST['work_kind']
        homework.allow_resubmit = True if request.POST['allow_resubmit'] == '1' else False
        homework.allow_random = True if request.POST['allow_random'] == '1' else False
        homework.allow_similarity = True if request.POST['allow_similarity'] == '1' else False
        # 新增
        homework.resubmit_number = request.POST['resubmit_number']
        homework.show_answer = request.POST['show_answer']
        homework.show_score = request.POST['show_score']
        homework.save()
        return redirect(reverse('homework_detail', args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id,
                   'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改公共作业" ' + homework.name + '"',
                   'work_kind': homework.work_kind,
                   'resubmit_number': homework.resubmit_number,
                   'allow_random': '1' if homework.allow_random else '0',
                   'allow_similarity': '1' if homework.allow_similarity else '0',
                   'allow_resubmit': '1' if homework.allow_resubmit else '0',
	               'show_answer': homework.show_answer,
                   'show_score': homework.show_score}
    return render(request, 'homework_add.html', context=context)

def update_my_homework(request, pk):
    """
    更新私有作业
    :param request: 请求
    :param pk: 私有作业主键
    :return: 私有作业详细页面
    """
    homework = get_object_or_404(MyHomework, pk=pk)
    try:
        if request.user != homework.creater and request.user.is_admin!=True:
            raise PermissionDenied
    except:
        raise PermissionDenied
    if request.method == 'POST':
        homework.name = request.POST['name']
        homework.choice_problem_ids = request.POST['choice-problem-ids']
        homework.ducheng_problem_ids=request.POST['ducheng-problem-ids']
        homework.problem_ids = request.POST['problem-ids']
        homework.tiankong_problem_ids = request.POST['tiankong-problem-ids']
        homework.gaicuo_problem_ids = request.POST['gaicuo-problem-ids']
        homework.courser = ClassName.objects.get(pk=request.POST['course'])
        homework.start_time = request.POST['start_time']
        homework.end_time = request.POST['end_time']
        homework.problem_info = request.POST['problem-info']
        homework.total_score = request.POST['total_score']
        homework.allowed_languages = ','.join(request.POST.getlist('languages'))
        homework.choice_problem_info = request.POST['choice-problem-info']
        homework.ducheng_problem_info=request.POST['ducheng-problem-info']
        homework.tiankong_problem_info = request.POST['tiankong-problem-info']
        homework.gaicuo_problem_info = request.POST['gaicuo-problem-info']
        homework.allow_resubmit = True if request.POST['allow_resubmit'] == '1' else False
        homework.allow_random = True if request.POST['allow_random'] == '1' else False
        homework.allow_similarity = True if request.POST['allow_similarity'] == '1' else False
        homework.show_answer = request.POST['show_answer']
        homework.show_score = request.POST['show_score']
        homework.work_kind = request.POST['work_kind']
        # 2017年9月新增功能
        tiankong_problem_ids = request.POST['tiankong-problem-ids']
        gaicuo_problem_ids = request.POST['gaicuo-problem-ids']
        # 新增
        homework.resubmit_number = request.POST['resubmit_number']
        homework.save()
        return redirect(reverse('my_homework_detail', args=[homework.pk]))
    else:
        context = {'languages': homework.allowed_languages, 'classnames': ClassName.objects.all(),
                   'name': homework.name, 'courser_id': homework.courser.id, 'start_time': homework.start_time,
                   'end_time': homework.end_time, 'title': '修改我的作业"' + homework.name + '"',
                   'resubmit_number': homework.resubmit_number,
                   'allow_resubmit': '1' if homework.allow_resubmit else '0',
                   'allow_random': '1' if homework.allow_random else '0',
                   'allow_similarity': '1' if homework.allow_similarity else '0',
                   'show_answer': homework.show_answer,
                   'show_score': homework.show_score,
                   'work_kind': homework.work_kind}
    return render(request, 'homework_add.html', context=context)  # 查看作业结果

@login_required()
def show_homework_result(request, id=0):
    """
    显示作业结果
    :param request: 请求
    :param id: 作业答案逐渐值
    :return: 作业结果详细页面
    """
    homework_answer = get_object_or_404(HomeworkAnswer, pk=id)

    if request.user != homework_answer.creator and homework_answer.homework.creater != request.user and (
            not request.user.is_superuser):  # 检测用户是否有权查看
        return render(request, 'warning.html', context={'info': '您无权查看其他同学的作业结果'})
    if not homework_answer.judged:  # 如果作业还未批改完成
        return render(request, 'information.html', context={'info': '作业正在批改,请稍后刷新查看或到已完成作业列表中查看'})
    # 作业批改完成而且用户有权查看时
    wrong_id = homework_answer.wrong_choice_problems.split(',')  # todo 应该该讲两个字段合并
    wrong_info = homework_answer.wrong_choice_problems_info.split(',')
    wrong_ducheng_id = homework_answer.wrong_ducheng_problems.split(',')  # todo 应该该讲两个字段合并
    wrong_ducheng_info = homework_answer.wrong_ducheng_problems_info.split(',')
    homework = homework_answer.homework
    homework_answers = homework.homeworkanswer_set.all().order_by('create_time')
    banjiList = []
    for banji in homework.banji.all():
        students = banji.students.all()
        if homework_answer.creator in students:
            banjiList.append(banji.id)
            break
    homewoek_answers = homework_answers.filter(creator__banJi_students__in=BanJi.objects.filter(id__in=banjiList))
    choice_problems = []
    ducheng_problems = []
    problems = []
    tiankong_problems = []
    gaicuo_problems = []
    allow_similarity = MyHomework.objects.get(pk=homework_answer.homework_id).allow_similarity
    show_answer = homework.show_answer  # 答案显示时机
    remained_number = homework_answer.remained_number  # 已经提交次数
    resubmit_number = homework.resubmit_number # 提交次数限制
    is_end = False if homework.start_time < timezone.now() < homework.end_time else True  # 作业是否截止

    for info in json.loads(homework.choice_problem_info):  # 载入作业的选择题信息，并进行遍历
        if str(info['id']) in wrong_id:  # 如果答案有错
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': False,
                 'info': wrong_info[wrong_id.index(str(info['id']))]})
        else:  # 如果答案正确
            choice_problems.append(
                {'detail': ChoiceProblem.objects.get(pk=info['id']), 'right': True})

    if not homework.ducheng_problem_info:
        homework.ducheng_problem_info = '[]'
    for info in json.loads(homework.ducheng_problem_info):  # 载入作业的填空题信息，并进行遍历
        # 更改读程题答案显示样式
        if str(info['id']) in wrong_ducheng_id:  # 如果答案有错
            ducheng_problems.append(
                {'detail': DuchengProblem.objects.get(pk=info['id']), 'right': False,
                 'info': wrong_ducheng_info[wrong_ducheng_id.index(str(info['id']))]})
        else:  # 如果答案正确
            ducheng_problems.append(
                {'detail': DuchengProblem.objects.get(pk=info['id']), 'right': True})

    # 获得编程题
    try:
        problem_ids = list(map(int, homework.problem_ids.split(",")))
    except:
        problem_ids = []
    info = json.loads(homework.problem_info)
    for pid in problem_ids:
        result = 0
        for inf in info:
            if inf['id'] == pid:
                total_score = int(inf['total_score'])
        similar_code_owners = []
        try:
            solution = Solution.objects.get(problem_id=pid,homework_answer=homework_answer)
            result = solution.result
            try:
                sourceCode = SourceCode.objects.get(solution_id=solution.solution_id).source
            except ObjectDoesNotExist:
                sourceCode = "代码未找到"
            try:
                if allow_similarity:
                    if result == 4:
                        score = total_score
                    else:
                        score = int(get_similarity(solution.solution_id)*total_score)
                else:
                    if result == 4:
                        score = total_score
                    else:
                        score = 0
                if request.user.isTeacher() :
                    for homework_answer_compare in homework_answers:
                        solution_compare = Solution.objects.get(problem_id=pid, homework_answer=homework_answer_compare)
                        if solution_compare.solution_id == solution.solution_id:
                            continue
                        try:
                            sourceCode_compare = SourceCode.objects.get(solution_id=solution_compare.solution_id).source
                            # 如果用于比较的代码早于此题的代码提交且相似度高于0.8
                            if get_similarity_v2(sourceCode,sourceCode_compare) >= 0.9:
                                similar_code_owners.append({'id_num': homework_answer_compare.creator.id_num,
                                                            'username': homework_answer_compare.creator.username,
                                                            'homework_answer_compare_id':homework_answer_compare.id})
                        except ObjectDoesNotExist:
                            sourceCode_compare = "用于比较的代码未找到"
            except:
                score = 0
        except:
            sourceCode = "未回答"
            score = 0
        problem = Problem.objects.get(pk=pid)
        problems.append({'code': sourceCode, 'desc': problem.description,
                         'title': problem.title, 'result': result,'score': score,
                         'total_score':total_score, 'p_id':pid,
                         'similar_code_owners': similar_code_owners})
    #获得程序填空题
    try:
        tiankong_ids = list(map(int,homework.tiankong_problem_ids.split(",")))
    except:
        tiankong_ids = []
    for pid in tiankong_ids:
        result = 0
        try:
            solution = Solution.objects.get(problem_id=pid,homework_answer=homework_answer)
            result = solution.result
            try:
                sourceCode = SourceCode.objects.get(solution_id=solution.solution_id).source
            except ObjectDoesNotExist:
                sourceCode = "代码未找到"
        except:
            sourceCode = "未回答"
        problem = Problem.objects.get(pk=pid)
        tiankong_problems.append({'code': sourceCode, 'desc': problem.description,
                         'title': problem.title, 'result': result})
    #获得程序改错题
    try:
        gaicuo_ids = list(map(int,homework.gaicuo_problem_ids.split(",")))
    except:
        gaicuo_ids = []
    for pid in gaicuo_ids:
        result = 0
        try:
            solution = Solution.objects.get(problem_id=pid,homework_answer=homework_answer)
            result = solution.result
            try:
                sourceCode = SourceCode.objects.get(solution_id=solution.solution_id).source
            except ObjectDoesNotExist:
                sourceCode = "代码未找到"
        except:
            sourceCode = "未回答"
        problem = Problem.objects.get(pk=solution.problem_id)
        gaicuo_problems.append({'code': sourceCode, 'desc': problem.description,
                         'title': problem.title, 'result': result})
    if not homework_answer.score_list:
        current_score = homework_answer.score
    else:
        current_score = homework_answer.score_list.split(',')[-2]
    context={'choice_problems': choice_problems, 'problem_score': homework_answer.problem_score,
                       'ducheng_problems': ducheng_problems,
                       'choice_problem_score': homework_answer.choice_problem_score,
                       'ducheng_problem_score': homework_answer.ducheng_problem_score,
                       'gaicuo_score': homework_answer.gaicuo_score,
                       'tiankong_score':homework_answer.tiankong_score,
                       'current_score': int(current_score), 'problems': problems,
                       'tiankong_problems': tiankong_problems, 'gaicuo_problems': gaicuo_problems,
                       'work_kind': homework.work_kind, 'summary': homework_answer.summary,
                       'teacher_comment': homework_answer.teacher_comment,
                       'allow_similarity': allow_similarity,
                       'title': ' {}的"{}"详细'.format(homework_answer.creator.username, homework.name),
                       'show_answer': show_answer, 'remained_number': remained_number,
                       'resubmit_number': resubmit_number, 'is_end': is_end}
    #logger.info(str(context))
    #mxy
    log = "执行动作：查看作业详细，用户信息：{}({}:{})，详细：{}".format(request.user.username, request.user.pk, request.user.id_num, t)
    logger.info(log + "执行结果：成功")
    return render(request, 'homework_result.html',context)

def get_choice_score(homework_answer):
    """
    获取选择题成绩
    :param homework_answer: 需要获取成绩的作业答案
    :return: 选择题成绩
    """
    choice_problem_score = 0
    if homework_answer.homework.choice_problem_info is not None:
        for info in json.loads(homework_answer.homework.choice_problem_info):  # 获取并遍历所属作业的选择题信息
            if str(info['id']) not in homework_answer.wrong_choice_problems.split(','):  # 如果答案正确
                choice_problem_score += int(info['total_score'])
    return choice_problem_score

def get_ducheng_score(homework_answer):
    """
    获取读程题成绩
    :param homework_answer: 需要获取成绩的作业答案
    :return: 选择题成绩
    """
    ducheng_problem_score = 0
    if homework_answer.homework.ducheng_problem_info is not None:
        for info in json.loads(homework_answer.homework.ducheng_problem_info):  # 获取并遍历所属作业的读程题信息
            if str(info['id']) not in homework_answer.wrong_ducheng_problems.split(','):  # 如果答案正确
                ducheng_problem_score += int(info['total_score'])
    return ducheng_problem_score

# 显示作业并处理作业答案
@login_required()
def do_homework(request, homework_id=0):
    """
    做题
    :param request: 请求
    :param homework_id:作业的id
    :return: 重定向
    """
    if request.method == 'POST':  # 当提交作业时
        wrong_ids, wrong_info = '', ''
        wrong_ducheng_ids, wrong_ducheng_info = '', ''
        homework = get_object_or_404(MyHomework, pk=homework_id)
        log = "执行动作：提交作业，用户信息：{}({}:{})，作业ID：{}，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,homework_id,request.POST.dict())
        if time.mktime(homework.end_time.timetuple()) < time.time():
            logger.info(log + "，执行结果：失败（时间不允许）")
            return render(request, 'warning.html', context={'info': '提交时间晚于作业的截止时间，提交失败'})
        if not homework.allow_resubmit:
            if request.user in homework.finished_students.all():  # 防止重复提交
                logger.info(log + "，执行结果：失败（重复提交）")
                return render(request, 'warning.html', context={'info': '您已提交过此题目，请勿重复提交'})
            else:
                homework.finished_students.add(request.user)
                try:
                    HomeworkAnswer.objects.get(homework=homework, creator=request.user)
                    logger.info(log + "，执行结果：失败（重复提交）")
                    return render(request, 'warning.html', context={'info': '您已提交过此题目，请勿重复提交'})
                except ObjectDoesNotExist:
                    pass
            homeworkAnswer = HomeworkAnswer(creator=request.user, homework=homework)
        else:
            homeworkAnswers = HomeworkAnswer.objects.filter(creator=request.user, homework=homework)
            if homeworkAnswers:
                for homeworkAnswer in homeworkAnswers:
                    for solution in homeworkAnswer.solution_set.all():
                        SourceCode.objects.get(solution_id=solution.solution_id).delete()
                        solution.delete()
                    homeworkAnswer.judged = False
            else:
                homework.finished_students.add(request.user)
                # 新增
                homeworkAnswer = HomeworkAnswer(creator=request.user, homework=homework)
                homeworkAnswer.remained_number = 0
        homeworkAnswer.remained_number += 1
        homeworkAnswer.save()

        # 判断选择题，保存错误选择题到目录
        for id in homework.choice_problem_ids.split(','):
            if id and request.POST.get('selection-' + id, 'x') != ChoiceProblem.objects.get(pk=id).right_answer:
                wrong_ids += id + ','  # 保存错误题目id
                wrong_info += request.POST.get('selection-' + id, '未回答') + ','  # 保存其回答记录
        # 判断填空题，保存错误读程题到目录
        if homework.ducheng_problem_ids:
            for id in homework.ducheng_problem_ids.split(','):
                if id and request.POST.get(id) not in (DuchengProblem.objects.get(pk=id).answer).split('|||'):  
                    wrong_ducheng_ids += id + ','  # 保存错误题目id
                    wrong_ducheng_info += request.POST.get('selection-' + id, '未回答') + ','  # 保存其回答记录
        # 创建编程题的solution，等待oj后台轮询判题
        # output = open('/tmp/error.log', 'w')
        for k, v in request.POST.items():
            # 如果有代码提交过来
            if k.startswith('source'):
                # 如果提交的代码已经存在于Solution表中，则读取表中数据
                needNewSolution = False
                if request.POST['solution-' + k[7:]]:
                    try:
                        solution = Solution.objects.get(solution_id=request.POST['solution-' + k[7:]])
                    except ObjectDoesNotExist :
                        needNewSolution = True
                    except ValueError :
                        needNewSolution = True
                else:
                    needNewSolution = True

                if needNewSolution :
                    # 否则，创建新的Solution数据
                    code = v if v else  "未回答"
                    solution = Solution(problem_id=k[7:], user_id=request.user.username,
                                language=request.POST['language-' + k[7:]], ip=request.META['REMOTE_ADDR'],
                                code_length=len(v))
                    # 如果提交的代码为空，则默认为错误结果，无需交给判题程序
                    if not v :
                        solution.result = 6
                    solution.save()
                    # 将代码存到Code表中
                    source_code = SourceCode(solution_id=solution.solution_id, source=code)
                    source_code.save()
                homeworkAnswer.solution_set.add(solution)
        homeworkAnswer.wrong_choice_problems = wrong_ids
        homeworkAnswer.wrong_choice_problems_info = wrong_info
        try:
            homeworkAnswer.summary = request.POST['summary']
        except:
            pass
        homeworkAnswer.save()
        logger.info(log + "，执行结果：成功")
        # output.close()
        homeworkAnswer.wrong_ducheng_problems = wrong_ducheng_ids
        homeworkAnswer.wrong_ducheng_problems_info = wrong_ducheng_info
        # 开启判题进程，保存编程题目分数
        _thread.start_new_thread(judge_homework, (homeworkAnswer,))
        try:  # 如果有暂存的该作业答案，删除掉
            log = "执行动作：删除暂存作业，用户信息：{}({}:{})，作业ID：{}".format(request.user.username,request.user.pk,request.user.id_num,homework)
            TempHomeworkAnswer.objects.get(creator=request.user, homework=homework).delete()
            logger.info(log + "，执行结果：成功")
        except ObjectDoesNotExist:
            logger.info(log + "，执行结果：无暂存作业")
        return redirect(reverse('show_homework_result', args=[homeworkAnswer.id]))
    else:  # 当正常访问时
        homework = get_object_or_404(MyHomework, pk=homework_id)
        log = "执行动作：打开作业，用户信息：{}({}:{})，作业ID：{}".format(request.user.username,request.user.pk,request.user.id_num,homework_id)
        choice_problems = []
        if homework.choice_problem_ids is not None:
            for id in homework.choice_problem_ids.split(','):
                if id:
                    try:
                        choice_problems.append({'detail': ChoiceProblem.objects.get(pk=id),
                                                'score': json.loads(homework.choice_problem_info)[0]['total_score']})
                    except ObjectDoesNotExist:
                       return render(request, 'warning.html', context={
            'info': '对不起，本作业(ID={})中请求的填空题(ID={})不在题库中，请及时联系管理员：'.format(homework_id,id) + settings.CONTACT_INFO})
        if homework.allow_random:
            random.shuffle(choice_problems)
        ducheng_problems = []
        if homework.ducheng_problem_ids is not None:
            for id in homework.ducheng_problem_ids.split(','):
                if id:
                    try:
                        ducheng_problems.append({'detail':DuchengProblem.objects.get(pk=id),
                                                 'score': json.loads(homework.ducheng_problem_info)[0]['total_score']})
                    except ObjectDoesNotExist:
                       return render(request, 'warning.html', context={
            'info': '对不起，本作业(ID={})中请求的读程题(ID={})不在题库中，请及时联系管理员：'.format(homework_id,id) + settings.CONTACT_INFO})
        
        problems = []
        if homework.problem_ids is not None:
            for id in homework.problem_ids.split(','):
                if id:
                    try:
                        problems.append(Problem.objects.get(pk=id))
                    except ObjectDoesNotExist:
                       return render(request, 'warning.html', context={
            'info': '对不起，本作业(ID={})中请求的编程题(ID={})不在题库中，请及时联系管理员：'.format(homework_id,id) + settings.CONTACT_INFO}) 
        tiankong_problems = []
        if homework.tiankong_problem_ids is not None:
            for id in homework.tiankong_problem_ids.split(','):
                if id:
                    try:
                        tiankong_problems.append(Problem.objects.get(pk=id))
                    except ObjectDoesNotExist:
                       return render(request, 'warning.html', context={
            'info': '对不起，本作业(ID={})中请求的程序填空题(ID={})不在题库中，请及时联系管理员：'.format(homework_id,id) + settings.CONTACT_INFO})
        gaicuo_problems = []
        if homework.gaicuo_problem_ids is not None:
            for id in homework.gaicuo_problem_ids.split(','):
                if id:
                    try:
                        gaicuo_problems.append(Problem.objects.get(pk=id))
                    except ObjectDoesNotExist:
                       return render(request, 'warning.html', context={
            'info': '对不起，本作业(ID={})中请求的程序改错题(ID={})不在题库中，请及时联系管理员：'.format(homework_id,id) + settings.CONTACT_INFO})
        logger.info(log + "，执行结果：成功")
        # 新增
        # try:
        homeworkAnswers = HomeworkAnswer.objects.filter(creator=request.user, homework=homework)
        if len(homeworkAnswers) == 0:
            remained_number = homework.resubmit_number
        else:
            last_homeworkAnswer = homeworkAnswers.order_by('-create_time') [0]
            remained_number = homework.resubmit_number - last_homeworkAnswer.remained_number
        # 第一次请求作业

        if remained_number <= 0:
            logger.info(log + "，执行结果：失败（提交次数达上限）")
            return render(request, 'warning.html', context={'info': '您的提交次数已达上限！'})
        else:
            return render(request, 'do_homework.html',
                        context={'homework': homework, 'problemsType': ['编程题','程序填空题','程序改错题'],
                                'choice_problems': choice_problems,
                                'ducheng_problems': ducheng_problems,
                                'problemsList':[problems, tiankong_problems, gaicuo_problems],
                                'title': homework.name, 'work_kind': homework.work_kind, 'remained_number': remained_number})

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


@permission_required('judge.add_classname')
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

@permission_required('work.add_banji')
def get_assign_status(request):
    """
    处理获取班级列表信息的ajax请求，包含作业的布置状态
    :param request: 请求
    :return: 含有班级列表信息的json
    """
    json_data = {}
    records = []
    kwargs = {}
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    homework_id = request.GET.get('homework_id','')
    if homework_id=='': 
        return JsonResponse(json_data)
    homework_id = int(homework_id)
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
        homework = MyHomework.objects.get(pk=homework_id)
        record = {'name': banji.name, 'pk': banji.pk,
                  'courser': banji.courser.name, 'id': banji.pk, 'teacher': banji.teacher.username,
                  'start_time': banji.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'end_time': banji.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                  'status': homework in banji.myhomework_set.all()}
        logger.info(record)
        records.append(record)
    json_data['rows'] = records
    return JsonResponse(json_data)

# 删除班级
@permission_required('work.delete_banji')
def del_banji(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                banji = BanJi.objects.get(pk=pk)
                if request.user == banji.teacher or request.user.is_admin:
                    banji.delete()
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
                                  start_time=time.strftime("%Y-%m-%d %H:%M"), 
                                  end_time=(datetime.datetime.now()+datetime.timedelta(days=14)).strftime("%Y-%m-%d %H:%M"),
                                  problem_ids=old_homework.problem_ids,
                                  choice_problem_ids=old_homework.choice_problem_ids,
                                  ducheng_problem_ids=old_homework.ducheng_problem_ids,
                                  problem_info=old_homework.problem_info,
                                  choice_problem_info=old_homework.choice_problem_info,
                                  ducheng_problem_info=old_homework.ducheng_problem_info,
                                  #2017年9月16日增加新题型
                                  tiankong_problem_ids=old_homework.tiankong_problem_ids,
                                  gaicuo_problem_ids=old_homework.gaicuo_problem_ids,
                                  tiankong_problem_info=old_homework.tiankong_problem_info,
                                  gaicuo_problem_info=old_homework.gaicuo_problem_info,
                                  allowed_languages=old_homework.allowed_languages,
                                  allow_resubmit=old_homework.allow_resubmit,
                                  allow_similarity=old_homework.allow_similarity,
                                  allow_random=old_homework.allow_random,
                                  work_kind=old_homework.work_kind,
                                  total_score=old_homework.total_score,  # todo 有更好的方法
                                  resubmit_number = old_homework.resubmit_number,
                                  show_answer = old_homework.show_answer,
                                  show_score = old_homework.show_score)
            homework.save()
    except:
        logger_request.exception("Exception Logged")
        return HttpResponse(0)
    return HttpResponse(1)


@permission_required('work.add_homework')
def list_my_homework(request):
    classnames = ClassName.objects.all()
    context = {'classnames': classnames, 'title': '我的私有作业列表', 'position': 'private_work_manage'}
    return render(request, 'my_homework_list.html', context=context)



@permission_required('work.add_banji')
def show_banji(request, pk):
    """
    :return:a list like [{"name":"mike","grades":[100,200,300,400]},{...},...],score is sorted by homework's start time
    """
    banji = get_object_or_404(BanJi, pk=pk)
    students_scores = []
    students = banji.students.all()
    homeworks = banji.myhomework_set.all().order_by('start_time')
    students_scores = []
    #for student in students:
    #    info = {'name': student.username}
    #    info['id'] = student.id_num
    #    scores = []
    #    for index, homework in enumerate(homeworks):
    #        answers = homework.homeworkanswer_set.all()
    #        scores.append(answers.get(
    #            creator=student).score if student in homework.finished_students.all() else "无")
    #    info['scores'] = scores
    #    students_scores.append(info)
    context = {'id': banji.id, 'name': banji.name, 'courser': banji.courser.name, 'start_time': banji.start_time,
               'end_time': banji.end_time, 'teacher': banji.teacher.username,
               'title': '班级"' + banji.name + '"的信息', 'scores': students_scores}
    return render(request, 'banji_detail.html', context=context)

@login_required()
def get_students(request,banji=None):
    json_data = {}
    if banji!=None and banji!='':
        banji = BanJi.objects.get(pk=banji)
    else:
        return HttpResponse(json.dumps(json_data))
    users = banji.students
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    try:
        qset = ( Q(username__icontains=request.GET['search']) |
                 Q(email__icontains=request.GET['search']) |
                 Q(id_num__icontains=request.GET['search']) )
        users = users.filter(qset)
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'id_num'
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    json_data['total'] = users.count()
    for user in users.all().order_by(sort)[offset:offset + limit]:
        recode = {'username': user.username, 'pk': user.pk,
                  'email': user.email, 'id_num': user.id_num, 'group': user.groups.all()[0].name, 'id': user.pk}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))

@permission_required('work.change_banji')
def add_students(request, pk):
    teacher = MyUser.objects.get(id=request.user.id)
    return render(request, 'add_students.html', context={'id': pk, 'teacher':teacher, 'title': '添加学生到班级'})


@permission_required('work.change_banji')
def ajax_add_students(request):
    stu_detail = request.POST['stu_detail']
    banji_id = request.POST['banji_id']
    teacher = MyUser.objects.get(id=request.user.id)
    allow_num = teacher.allow_num
    if teacher.create_num < 1:
        return HttpResponse(json.dumps({'result': 0, 'count': 0, 'allow': 1,'message':'已达到允许添加学生数量上限'}))
    if len(stu_detail.split()) > 1:
        id_num, username = stu_detail.split()[0], stu_detail.split()[1]
        if teacher.school == '' and teacher.school_short == '':
            try:
                student = MyUser.objects.get(id_num=id_num)
                if student.username == username:
                    student.groups.add(Group.objects.get(name='学生'))
                else:
                    return HttpResponse(json.dumps({'result': 0, 'count': 0, 'allow': 1,'message':'该学号被其他用户占用，请联系管理员老师'}))
                #if student.username != username:
                #    student = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
                #    student.set_password(id_num)
                #    student.save()
                #    student.groups.add(Group.objects.get(name='学生'))
            except:
                student = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
                student.set_password(id_num)
                student.save()
                student.groups.add(Group.objects.get(name='学生'))
            
        else:
            try:
                student = MyUser.objects.get(id_num=teacher.school_short+id_num)
                if student.username == username:
                    student.groups.add(Group.objects.get(name='学生'))
                else:
                    return HttpResponse(json.dumps({'result': 0, 'count': 0, 'allow': 1,'message':'该学号被占用'}))
                #if student.username != username:
                #    student = MyUser(id_num=teacher.school_short+id_num, email=id_num + '@' + teacher.school_short.lower() + '.edu.cn', username=username, school=teacher.school, school_short=teacher.school_short)
                #    student.set_password(teacher.school_short+id_num)
                #    student.save()
                #    student.groups.add(Group.objects.get(name='学生'))
            except:
                if len(MyUser.objects.filter(email=id_num + '@' + teacher.school_short.lower() + '.edu.cn'))==0:
                    student = MyUser(id_num=teacher.school_short+id_num, email=id_num + '@' + teacher.school_short.lower() + '.edu.cn', username=username, school=teacher.school, school_short=teacher.school_short)
                    student.set_password(teacher.school_short+id_num)
                    student.save()
                    student.groups.add(Group.objects.get(name='学生'))
                else:
                    return HttpResponse(json.dumps({'result': 0, 'count': 0, 'allow': 1,'message':'该邮箱被占用'}))
    banji = BanJi.objects.get(pk=banji_id)
    if teacher.create_num > 0:
        banji.students.add(student)
        teacher.create_num -= 1
        teacher.save()
        return HttpResponse(json.dumps({'result': 0, 'count': 1}))


def reset_stupassword(request):
    if request.method == 'POST':
        stu_id = request.POST.get('id')
        banji_id = request.POST.get('banji_id')
        try:
            student = MyUser.objects.get(pk=stu_id)
            banji = BanJi.objects.get(pk=banji_id)
            if student.isTeacher():#不允许重置教师账号的密码
                return HttpResponse(2)
            stu_nu = student.id_num
            student.set_password(stu_nu)
            student.save()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)

def del_students(request):
    if request.method == 'POST':
        stu_id = request.POST.get('id')
        banji_id = request.POST.get('banji_id')
        try:
            student = MyUser.objects.get(pk=stu_id)
            banji = BanJi.objects.get(pk=banji_id)
            if banji.teacher==student:
                return HttpResponse(2)
            banji.students.remove(student)
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)

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

@permission_required('work.add_homework')
def unassign_homework(request):
    homework_id = request.POST['homework_id']
    banji_id = request.POST['id']
    try:
        homework = MyHomework.objects.get(pk=homework_id)
        banji = BanJi.objects.get(pk=banji_id)
        banji.myhomework_set.remove(homework)
        return HttpResponse(json.dumps({'result': 0, 'count': 1}))
    except:
        return HttpResponse(json.dumps({'result': 0, 'message': '出错了'}))

# 显示我的待做作业
@login_required()
def list_do_homework(request):
    banjis = BanJi.objects.filter(students=request.user).all()
    return render(request, 'do_homework_list.html',
                  context={'banjis': banjis, 'title': '我的作业列表', 'position': 'unfinished'})

# 获取待做作业列表
@login_required()
def get_my_homework_todo(request):
    log = "执行动作：读取作业列表，用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict())
    #mxy
    logger.info(log+"执行结果：成功")
    user = request.user
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    banji = request.GET['banji']
    count = 0
    #homeworks = MyHomework.objects.filter(banji__students=user)

    if banji != '0' and banji != '':
        homeworks = MyHomework.objects.filter(banji__id=banji)
    else:
        banji = BanJi.objects.filter(students=user,end_time__gte=datetime.datetime.now())
        homeworks = MyHomework.objects.filter(banji__id__in=banji)

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
    #重复作业项目去重，不同班级中若布置了同一作业，只显示一次
    listed = []
    for homework in homeworks.all().order_by(sort):
        if homework.pk in listed :
            continue
        else :
            listed.append(homework.pk)

        if (request.user in homework.finished_students.all()):
            #查找对应作业的分数
            homework_answers = HomeworkAnswer.objects.filter(creator=user,homework_id=homework.pk).order_by('-create_time')
            if homework_answers.exists():
                homework_answer=homework_answers[0]
                if homework_answer.judged==1:
                    score = "{}/{}".format(homework_answer.score,homework.total_score)
                else:
                    score = "批阅中"
            else:
                score = "批阅中"
            allow_resubmit = homework.allow_resubmit if (homework.start_time < timezone.now() < homework.end_time) else False
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework_answer.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'status': 1, 'score': score, 'allow_resubmit':allow_resubmit}
                      #status为1表示已完成
        elif not (homework.start_time < timezone.now() < homework.end_time):
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'status': -1}
                      #status为-1表示时间不允许
        elif TempHomeworkAnswer.objects.filter(homework_id=homework.pk, creator=request.user).exists(): 
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'status': 2}
                      #status为2表示开始做但是未提交
        else:
            recode = {'name': homework.name, 'pk': homework.pk,
                      'courser': homework.courser.name, 'id': homework.pk,
                      'start_time': homework.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'end_time': homework.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                      'status': 0}
                      #status为0表示未做

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
            # 根据测试用例获取编程题总分
            total_score = int(info['total_score'])
            for case in info['testcases']:  # 获取题目的测试分数
                if solution.result == 11 or solution.result == 6 or solution.result == 10:  # 如果题目出现编译错误或答案错误，可以根据相似度判分
                    if homework.allow_similarity == True:
                        id = solution.solution_id
                        score += int(total_score*get_similarity(id))
                        break
                    else:
                        break
                if solution.oi_info is None:
                    break
                if json.loads(solution.oi_info)[str(case['desc']) + '.in']['result'] == 4:  # 参照测试点，依次加测试点分数
                    score += int(case['score'])
            if solution.result == 4:
                id = solution.solution_id # 更新答案库
                update_ansdb(id)
        except ObjectDoesNotExist:
            user = homework_answer.creator;
            logger_request.exception("获取编程题得分失败{{homework_id:{},answer_id:{},problem_id:{},user:{}({},{})}}".format(homework.pk,homework_answer.pk,info['id'],user.username,user.id_num,user.email))
            #print("error on get problem score！homework_id: %d ,error : %s args: %s" % (
            #    homework.pk, e, e.args.__str__()))
    return score

def get_tiankong_score(homework_answer, judged_score=0):
    score = judged_score
    homework = homework_answer.homework
    solutions = homework_answer.solution_set
    tiankong_problem_info = []
    if homework.tiankong_problem_info:
        for info in json.loads(homework.tiankong_problem_info):
            try:
                solution = solutions.get(problem_id=info['id'])
                for case in info['testcases']:
                    if solution.result == 11:
                        break
                    if solution.oi_info is None:
                        break
                    if json.loads(solution.oi_info)[str(case['desc'])+'.in']['result'] == 4:
                        score += int(case['score'])
            except ObjectDoesNotExist:
                user = homework_answer.creator;
                logger_request.exception("获取程序填空题得分失败{{homework_id:{},answer_id:{},problem_id:{},user:{}({},{})}}".format(homework.pk,homework_answer.pk,info['id'],user.username,user.id_num,user.email))
    return score

def get_gaicuo_score(homework_answer, judged_score=0):
    score = judged_score
    homework = homework_answer.homework
    solutions = homework_answer.solution_set
    gaicuo_problem_info = []
    if homework.gaicuo_problem_info:
        try:
            for info in json.loads(homework.gaicuo_problem_info):
                solution = solutions.get(problem_id=info['id'])
                for case in info['testcases']:
                    if solution.result == 11:
                        break
                    if solution.oi_info is None:
                        break
                    if json.loads(solution.oi_info)[str(case['desc'])+'.in']['result'] == 4:
                        score += int(case['score'])
        except ObjectDoesNotExist:
            user = homework_answer.creator;
            logger_request.exception("获取程序改错题得分失败{{homework_id:{},answer_id:{},problem_id:{},user:{}({},{})}}".format(homework.pk,homework_answer.pk,info['id'],user.username,user.id_num,user.email))
    return score

@login_required()
def list_finished_homework(request):
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied
    banjis = BanJi.objects.filter(students=request.user).all()
    return render(request, 'finidshed_homework_list.html',
                  context={'classnames': banjis, 'position': 'finished', 'title': '查看作业结果'})


@login_required()
def get_finished_homework(request):
    """
    获取用户已经完成的作业记录
    :param request: 请求
    :return: 含有用户已完成作业的json
    """
    if not request.user.isTeacher() and not request.user.is_admin:
        raise PermissionDenied
    json_data = {}
    records = []
    user = request.user
    #offset = int(request.GET['offset'])
    #limit = int(request.GET['limit'])
    if request.GET['classname'] != '0':
        banji = BanJi.objects.get(pk=request.GET['classname'])
        homeworks = banji.myhomework_set.all().order_by('start_time')
        stuCount = 0
        for student in banji.students.all().order_by('id_num'):
            #筛除教师账号
            if student.groups.all()[0].pk==2 :
                count = 1
                record = {'id': student.id_num,
                          'name': student.username}
                for index, homework in enumerate(homeworks):
                    answers = homework.homeworkanswer_set.all()
                    answer = answers.filter(creator=student).order_by('-create_time') if student in homework.finished_students.all() else None
                    if answer :
                        answer = answer[0]
                        record['score' + str(count)] = {
                                'pk': answer.pk,
                                'score': answer.score,
                                'work_kind':homework.work_kind
                            }
                    else :
                        record['score' + str(count)] = {
                                'score': "无",
                                'work_kind':homework.work_kind
                            }
                    count = count + 1
                records.append(record)
                json_data['rows'] = records
                stuCount = stuCount + 1
        
        json_data['total'] = stuCount
    else :
        json_data['total'] = 0
        json_data['rows'] = {}
    return JsonResponse(json_data)

    #homework_answers = HomeworkAnswer.objects.filter(creator=user)
    #if request.GET['classname'] != '0':
    #    homework_answers = homework_answers.filter(homework__courser=HomeWork.objects.get(pk=request.GET['classname']))
    #try:
    #    homework_answers = homework_answers.filter(homework__name__icontains=request.GET['search'])
    #except:
    #    pass
    #try:
    #    sort = request.GET['sort']
    #except MultiValueDictKeyError:
    #    sort = 'pk'
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
    #return JsonResponse(json_data)

@permission_required('work.add_homework')
def get_finished_homework_workInformation(request):
    """
    在作业结果页面中返回作业的详细信息
    """
    json_data = {}
    record = []
    if request.GET.get('class_name','') != '0':
        banji = BanJi.objects.get(pk=request.GET['class_name'])
        homeworks = banji.myhomework_set.all().order_by('start_time')
        students = banji.students.all().order_by('id_num')
        stuCount = banji.students.all().count() - 1
        json_data['stuCount'] = stuCount
        i = 1  #计数实验次数
        j = 1  #计数作业次数
        json_data['实验'] = {}
        json_data['作业'] = {}
        for homework in homeworks:
            no_answer = 0  #没有写作业的人数
            for student in students:
                if student.groups.all()[0].pk == 2:
                    if not homework.finished_students.filter(id=student.id):
                            no_answer = no_answer + 1

            record.append(no_answer)
            record.append(homework.name)
            record.append(homework.total_score)
            record.append(homework.start_time.strftime('%Y-%m-%d %H:%M:%S'))
            record.append(homework.end_time.strftime('%Y-%m-%d %H:%M:%S')) 
            if homework.work_kind == '实验':
                json_data['实验'][str(i)] = record
                i = i + 1
            else:
                json_data['作业'][str(j)] = record
                j = j + 1
            record = []
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
    else:
        banjiList = []
        for banji in homework.banji.all():
            if time.mktime(banji.start_time.timetuple()) < time.time() < time.mktime(banji.end_time.timetuple()):
                banjiList.append(banji.pk)
        homework_answers = homework_answers.filter(
            creator__banJi_students__in=BanJi.objects.filter(id__in=banjiList))
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
        recode = {'creator__id_num': homework_answer.creator.id_num,
                  'username': homework_answer.creator.username,
                  'create_time': homework_answer.create_time.strftime('%Y-%m-%d %H:%M:%S'), 'id': homework_answer.id,
                  'teacher': 'dd',
                  'score': score
                  }
        if recode not in recodes:
            recodes.append(recode)
    json_data['rows'] = recodes
    return JsonResponse(json_data)


@permission_required('judge.add_classname')
def list_coursers(request):
    """
    列出课程
    """
    if not request.user.is_admin:
        raise PermissionDenied 
    coursers = ClassName.objects.all()
    return render(request, 'courser_list.html', {'coursers': coursers, 'title': '课程列表', 'position': 'courser_manage'})


@permission_required('judge.add_knowledgepoint1')
def list_kp1s(request, id):
    courser = get_object_or_404(ClassName, id=id)
    kp1s = KnowledgePoint1.objects.filter(classname=courser)
    return render(request, 'kp1_list.html', {'kp1s': kp1s, 'title': '查看课程“%s”的一级知识点' % courser.name, 'id': id})


@permission_required('judge.add_knowledgepoint2')
def list_kp2s(request, id):
    kp1 = get_object_or_404(KnowledgePoint1, id=id)
    kp2s = KnowledgePoint2.objects.filter(upperPoint=kp1)
    return render(request, 'kp2s_list.html', context={'kp2s': kp2s, 'id': id, 'title': '查看一级知识点"%s”下的二级知识点' % kp1.name})


@permission_required('judge.delete_classname')
def delete_courser(request):
    if not request.user.is_admin:
        raise PermissionDenied
    try:
        ClassName.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('judge.delete_knowledgepoint1')
def delete_kp1(request):
    if not request.user.is_admin:
        raise PermissionDenied
    try:
        KnowledgePoint1.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)

@permission_required('judge.delete_knowledgepoint2')
def delete_kp2(request):
    if not request.user.is_admin:
        raise PermissionDenied
    try:
        KnowledgePoint2.objects.get(id=request.POST['id']).delete()
        return HttpResponse(1)
    except:
        return HttpResponse(0)


@permission_required('judge.add_knowledgepoint1')
def add_kp1(request):
    if not request.user.is_admin:
        raise PermissionDenied
    kp1 = KnowledgePoint1(name=request.POST['name'], classname_id=request.POST['id'])
    kp1.save()
    return HttpResponse(1)


@permission_required('judge.add_knowledgepoint2')
def add_kp2(request):
    if not request.user.is_admin:
        raise PermissionDenied
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
            choice_problem_score = 0
            ducheng_problem_score = 0
            biancheng_score = 0
            tiankong_score = 0
            gaicuo_score = 0
            choice_problem_score = get_choice_score(homework_answer)  # 获取选择题分数
            homework_answer.choice_problem_score = choice_problem_score
            ducheng_problem_score = get_ducheng_score(homework_answer)  # 获取读程题分数
            homework_answer.ducheng_problem_score = ducheng_problem_score
            biancheng_score = get_problem_score(homework_answer)  # 获取编程题分数
            homework_answer.problem_score = biancheng_score
            #2017年9月16日增加新题型
            tiankong_score = get_tiankong_score(homework_answer)
            homework_answer.tiankong_score = tiankong_score
            gaicuo_score = get_gaicuo_score(homework_answer)
            homework_answer.gaicuo_score = gaicuo_score

            # 根据作业设置计算最终总分
            homework_answer.score_list += str(choice_problem_score + ducheng_problem_score + biancheng_score + tiankong_score + gaicuo_score) + ','  # 保存每次作业成绩
            zongfen_list = [int(zongfen) for zongfen in homework_answer.score_list.split(',')[:-1]]  # 转化为成绩列表
            show_score = get_object_or_404(MyHomework,pk=homework_answer.homework.id).show_score
            
            if show_score == '最高分值':
                zongfen = max(zongfen_list)
            elif show_score == '平均分值':
                zongfen = int(sum(zongfen_list)/len(zongfen_list) * 10 + 0.5) / 10 # 四舍五入
            else:
                zongfen = zongfen_list[-1]
            homework_answer.score = zongfen
            homework_answer.judged = True  # 修改判题标记为已经判过
            homework_answer.save()  # 保存
            logger.info("执行动作：计算成绩，用户信息：{}({}:{})，作业ID：{}，总分：{}(选择题：{}，读程题：{}，编程题：{}，程序填空题：{}，程序改错题：{})，执行结果：成功".format( \
                homework_answer.creator.username,homework_answer.creator.pk,homework_answer.creator.id_num,\
                homework_answer.homework,zongfen,choice_problem_score,ducheng_problem_score,biancheng_score,tiankong_score,gaicuo_score))
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
                              ducheng_problem_ids=request.POST['ducheng-problem-ids'],
                              problem_ids=request.POST['problem-ids'],
                              problem_info=request.POST['problem-info'],
                              choice_problem_info=request.POST['choice-problem-info'],
                              ducheng_problem_info=request.POST['ducheng-problem-info'],
                              courser=ClassName.objects.get(pk=request.POST['course']),
                              start_time=request.POST['start_time'],
                              end_time=request.POST['end_time'],
                              allowed_languages=','.join(request.POST.getlist('languages')),
                              total_score=request.POST['total_score'],
                              creater=request.user,
                              allow_resubmit=allow_resubmit,
                              resubmit_number = request.POST["resubmit_number"],
                              work_kind=request.POST['work_kind'],
                              show_answer = request.POST['show_answer'],
                              show_score = request.POST['show_score'])
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
            # SourceCode.objects.get(solution_id=solution.solution_id).delete()
            # solution.delete()
            try:
                compile_info = Compileinfo.objects.get(
                    solution_id=request.POST['solution_id']).error
            except:
                compile_info = ''
            return JsonResponse(
                {'status': 1, 'result': 0, 'info': {'info': '编译出错:\n' + compile_info, 'score': 0}})
        elif solution.result == 5: # 当出现格式错误的时候
            return JsonResponse(
                {'status': 1, 'result': 0, 'info': {'info': '格式错误:请使用题目中给定的输出格式输出结果，特别注意空格的位置和数量。', 'score': 0}})
        else:  # 当成功编译时
            result = 2  # 2代表通过全部测试用例
            right_num = wrong_num = 0  # 通过的测试点数量和未通过的测试点数量
            problem = Problem.objects.get(pk=request.POST['problem_id'])
            #cases = get_testCases(problem)
            cases = []
            score = 0
            infos = []
            if homework.problem_info:
                infos = infos + json.loads(homework.problem_info)
            if homework.gaicuo_problem_info:
                infos = infos + json.loads(homework.gaicuo_problem_info)
            if homework.tiankong_problem_info:
                infos = infos + json.loads(homework.tiankong_problem_info)
            for info in infos:
                if info['pk'] == solution.problem_id:
                    for case in info['testcases']:  # 获取题目的测试分数
                        try:
                            oi_info = json.loads(solution.oi_info)
                            if oi_info[str(case['desc']) + '.in']['result'] == 4:  # 参照测试点，依次加测试点分数
                                case['result'] = True
                                score += int(case['score'])
                                right_num += 1
                            else:
                                case['result'] = False
                                wrong_num += 1
                                result = 1
                            cases.append(case)
                        except:
                            logger_request.exception("Exception Logged")
            #2017年3月22日，注释以下两句，保留学生做作业的过程
            #SourceCode.objects.get(solution_id=solution.solution_id).delete()
            #solution.delete()
            return JsonResponse({'status': 1, 'result': result,
                                 'info': {'total_cases': len(cases), 'right_num': right_num,
                                          'wrong_num': wrong_num, 'score': score},
                                 'testcase': cases})

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
    #for solution in homeworkanswer.solution_set.all():
    #    SourceCode.objects.get(solution_id=solution.solution_id).delete()
    #    solution.delete()
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

@login_required()
def save_homework_temp(request):
    """
    暂存作业
    :param request: 请求
    :return: 重定向到作业列表
    """
    log = "执行动作：暂存作业，用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict())
    data = request.POST.dict()
    if data:
        try:
            homework = MyHomework.objects.get(id=data['homework_id'])
            del data['csrfmiddlewaretoken']  # 去除表单中的scrf项
            del data['homework_id']  # 去除表单中的homework_id项
            TempHomeworkAnswer.objects.update_or_create(homework=homework, creator=request.user,
                                                defaults={'data': json.dumps(data)})
            logger.info(log + "，执行结果：成功")
        except:
            logger_request.exception(log + "，执行结果：失败")
            return render(request, 'warning.html', context={
                'info': '对不起，暂存作业失败了，请及时联系管理员：' + settings.CONTACT_INFO})
    return redirect(reverse('list_do_homework'))


def init_homework_data(request):
    try:
        temp = TempHomeworkAnswer.objects.get(homework_id=request.POST['homework_id'], creator=request.user)
        return JsonResponse({'result': 1, 'data': json.loads(temp.data)})
    except Exception as e:
        return JsonResponse({'result': -1})


def file_download(request):
    return render(request, 'file_download.html', context={'title': '教学资源下载', 'position': 'source'})

@login_required()
def comment_change(request):
    if request.method == 'POST':
        answerId = request.POST['answerId']
        comment = request.POST['teacher_comment']
        change = request.POST['change']
        try:
            homework_answer = HomeworkAnswer.objects.filter(pk=answerId)
            if eval(change) == -1:
                homework_answer.update(teacher_comment=comment)
            else:
                homework_answer.update(teacher_comment=comment,score=change)
        except:
            pass
        return HttpResponse(1)

@login_required()
def send_zipfile(request,id):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    def zip_dir(dirname,zipfilename):
        filelist=[]
        if os.path.isfile(dirname):
            filelist.append(dirname)
        else:
            for root,dirs,files in os.walk(dirname):
                for name in files:
                    filelist.append(os.path.join(root,name))
        zf=zipfile.ZipFile(zipfilename,"w",zipfile.zlib.DEFLATED)
        for tar in filelist:
            arcname=tar[len(dirname):]
            zf.write(tar,arcname)
        zf.close()

    dirname='/home/judge/data/'+str(id)
    zipfilename='/tmp/'+str(id)+'.zip'
    zip_dir(dirname,zipfilename)

    the_file_name = zipfilename
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename=%s' %zipfilename
    return response

#mxy
@login_required()
def submit_homework_temp(request):
	radio_id = request.POST['radio_id']
	log = "执行动作：选择题点击操作，用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict())
	logger.info(log + "，执行结果：成功")
@login_required()
def mxy_click_temp(request):
    log = "执行动作：点击操作，用户信息：{}({}:{})，POST数据：{}".format(request.user.username,request.user.pk,request.user.id_num,request.POST.dict())
    logger.info(log+"，执行结果：成功")


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
