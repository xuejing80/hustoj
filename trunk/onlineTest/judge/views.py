# -*- coding: utf-8 -*-

import argparse
import codecs
import json
import os
import random
import re
import shutil
import string
import zipfile

from django.apps import apps
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.detail import DetailView

from judge.forms import ProblemAddForm, ChoiceAddForm
from .models import KnowledgePoint1, ClassName, ChoiceProblem, Problem

BUFSIZE = 4096
BOMLEN = len(codecs.BOM_UTF8)


# 添加编程题
@permission_required('judge.add_choiceproblem')
def add_choice(request):
    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            choice_problem = form.save(user=request.user)
            return redirect(reverse("choice_problem_detail", args=[choice_problem.id]))
    else:
        form = ChoiceAddForm()
    return render(request, 'choice_problem_add.html', {'form': form, 'title': '新建选择题'})


# 添加选择题
@permission_required('judge.add_problem')
def add_problem(request):
    if request.method == 'POST':  # 当提交表单时
        form = ProblemAddForm(request.POST)  # form 包含提交的数据
        if form.is_valid():  # 如果提交的数据合法
            problem = form.save(user=request.user)  # 保存题目
            old_path = '/tmp/' + request.POST['random_name'] + '/' + request.POST['file_name'] + '_files/'
            shutil.move(old_path, '/home/judge/data/')
            os.rename('/home/judge/data/' + request.POST['file_name'] + '_files',
                      '/home/judge/data/' + str(problem.problem_id))
            print(request.POST['random_name'])
            shutil.rmtree('/tmp/' + request.POST['random_name'])
            return redirect(reverse("problem_detail", args=[problem.problem_id]))
    else:  # 当正常访问时
        form = ProblemAddForm()
    return render(request, 'problem_add.html', {'form': form, 'title': '新建编程题'})


# 删除编程题
@permission_required('judge.delete_problem')
def delete_problem(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                if os.path.exists('/home/judge/data/' + str(pk)):
                    shutil.rmtree('/home/judge/data/' + str(pk))
                Problem.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 删除选择题
@permission_required('judge.delete_choiceproblem')
def del_choice_problem(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                ChoiceProblem.objects.filter(pk=pk).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)


# 处理选择知识点时的ajax请求
def select_point(request):
    response_data = {}
    course = request.POST.get('course', -1)
    parent = request.POST.get('parent', -1)

    if course == -1:
        point1 = KnowledgePoint1.objects.get(pk=parent)
        points = point1.knowledgepoint2_set
    else:
        course = ClassName.objects.get(pk=course)
        points = course.knowledgepoint1_set
    for point in points.all():
        response_data[point.id] = point.name
    return HttpResponse(json.dumps(response_data), content_type='application/json')


#  编程题详细视图
class ProblemDetailView(DetailView):
    model = Problem
    template_name = 'problem_detail.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super(ProblemDetailView, self).get_context_data(**kwargs)
        str = ''
        for point in self.object.knowledgePoint2.all():
            str += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '\n'
        context['knowledge_point'] = str
        context['title'] = '编程题“' + self.object.title + '”的详细信息'
        return context


# 选择题详细视图
class ChoiceProblemDetailView(DetailView):
    model = ChoiceProblem
    template_name = 'choice_problem_detail.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super(ChoiceProblemDetailView, self).get_context_data(**kwargs)
        str = ''
        for point in self.object.knowledgePoint2.all():
            str += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '\n'
        context['knowledge_point'] = str
        context['title'] = '选择题“' + self.object.title + '”的详细信息'
        return context


# 更新编程题
@permission_required('judge.change_problem')
def update_problem(request, id):
    problem = get_object_or_404(Problem, pk=id)
    json_dic = {}  # 知识点选择的需要的初始化数据
    for point in problem.knowledgePoint2.all():
        json_dic[point.id] = point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name
    initial = {'title': problem.title,
               'description': problem.description,
               'time_limit': problem.time_limit,
               'memory_limit': problem.memory_limit,
               'input': problem.input,
               'output': problem.output,
               'sample_input1': problem.sample_input,
               'sample_output1': problem.sample_output,
               'sample_input2': problem.sample_input2,
               'sample_output2': problem.sample_output2,
               'classname': 0,
               'keypoint': json.dumps(json_dic, ensure_ascii=False).encode('utf8')
               }  # 生成表单的初始化数据
    if request.method == "POST":  # 当提交表单时
        form = ProblemAddForm(request.POST)
        if form.is_valid():
            form.save(user=request.user, problemid=id)
            try:  # 对文件进行解压和保存
                old_path = '/tmp/' + request.POST['random_name'] + '/' + request.POST['file_name'] + '_files/'
                store_dir = '/home/judge/data/' + str(id)
                if os.path.exists(store_dir):
                    shutil.rmtree(store_dir)
                shutil.move(old_path, '/home/judge/data/')
                os.rename('/home/judge/data/' + request.POST['file_name'] + '_files',
                          '/home/judge/data/' + str(id))
                shutil.rmtree('/tmp/' + request.POST['random_name'])
            except Exception as  e:
                print(e)
                pass
            return redirect(reverse("problem_detail", args=[id]))
    return render(request, 'problem_add.html', {'form': ProblemAddForm(initial=initial)})


@permission_required('judge.change_choiceproblem')
def update_choice_problem(request, id):
    problem = get_object_or_404(ChoiceProblem, pk=id)
    json_dic = {}  # 知识点选择的需要的初始化数据
    for point in problem.knowledgePoint2.all():
        json_dic[point.id] = point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name
    initial = {'title': problem.title,
               'a': problem.a,
               'b': problem.b,
               'c': problem.c,
               'd': problem.d,
               'selection': problem.right_answer,
               'classname': 0,
               'keypoint': json.dumps(json_dic, ensure_ascii=False).encode('utf8')
               }  # 生成表单的初始化数据
    if request.method == "POST":  # 当提交表单时
        form = ChoiceAddForm(request.POST)
        if form.is_valid():
            form.save(user=request.user, id=id)
            return redirect(reverse("choice_problem_detail", args=[id]))
    return render(request, 'choice_problem_add.html', {'form': ChoiceAddForm(initial=initial)})


# 编程提列表
@permission_required('judge.add_problem')
def list_problems(request):
    classnames = ClassName.objects.all()
    return render(request, 'problem_list.html',
                  context={'classnames': classnames, 'title': '编程题题库', 'position': 'biancheng_list'})


# 选择题列表
@permission_required('judge.add_choiceproblem')
def list_choices(request):
    classnames = ClassName.objects.all()
    return render(request, 'choice_problem_list.html', context={'classnames': classnames, 'title': '选择题题库','position':'choice_list'})


# 返回含有问题数据的json
def get_json(request, model_name):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    knowledgePoint2 = request.GET['knowledgePoint2']
    classname = request.GET['classname']
    knowledgePoint1 = request.GET['knowledgePoint1']
    model = apps.get_model(app_label='judge', model_name=model_name)
    if knowledgePoint2 != '0':
        problems = model.objects.filter(knowledgePoint2__id=knowledgePoint2)
    elif knowledgePoint1 != '0':
        problems = model.objects.filter(knowledgePoint1__id=knowledgePoint1)
    elif classname != '0':
        problems = model.objects.filter(classname__id=classname)
    else:
        problems = model.objects
    try:
        problems = problems.filter(title__icontains=request.GET['search'])
    except:
        pass
    try:
        sort = request.GET['sort']
    except MultiValueDictKeyError:
        sort = 'pk'
    json_data['total'] = problems.count()
    if request.GET['order'] == 'desc':
        sort = '-' + sort
    for problem in problems.all().order_by(sort)[offset:offset + limit]:
        knowledge_point = ''
        if isinstance(problem, Problem):
            testCases = get_testCases(problem)
            total_score = get_totalScore(testCases)
        else:
            testCases = 0
            total_score = 5
        for point in problem.knowledgePoint2.all():
            knowledge_point += point.upperPoint.classname.name + ' > ' + point.upperPoint.name + ' > ' + point.name + '<br>'
        recode = {'title': problem.title, 'pk': problem.pk,
                  'update_date': problem.update_date.strftime('%Y-%m-%d %H:%M:%S'), 'id': problem.pk,
                  'knowledge_point': knowledge_point, 'testcases': testCases, 'total_score': total_score}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


# 获取指定题目的分值信息
def get_testCases(problem):
    """
    获取一道编程题的测试点信息
    :param problem: 带获取信息的题目
    :return: 以列表形式返回题目所有的测试点
    """
    cases = []
    r3 = re.compile('\d+ \d+ #.*#')
    r2 = re.compile('^\d+ \d+$')
    r22 = re.compile('^\d+ #.*#$')
    r1 = re.compile('^\d$')
    filename = '/home/judge/data/' + str(problem.problem_id) + "/scores.txt"
    try:
        with open(filename, 'rb') as f:
            data = f.read().decode('utf-8')
            if data[:3] == codecs.BOM_UTF8:  # 去除bom
                data = data[3:]
            lines = data.splitlines()
            i = 0
            for line in lines:
                if line:
                    try:
                        if r3.match(line):
                            score = int(line.split(maxsplit=2)[1])
                            desc = line.split(maxsplit=2)[0]
                            info = line.split(maxsplit=2)[2]
                            case = {'desc': desc, 'score': int(score), 'info': info}
                        elif r2.match(line):
                            score = int(line.split(maxsplit=1)[1])
                            desc = line.split(maxsplit=1)[0]
                            case = {'desc': desc, 'score': int(score), 'info': '没有提示信息'}
                        elif r22.match(line):
                            score = line.split(maxsplit=1)[0]
                            info = line.split(maxsplit=1)[1]
                            case = {'desc': i, 'score': int(score), 'info': info}
                        elif r1.match(line):
                            score = int(line.split(maxsplit=1)[0])
                            case = {'desc': i, 'score': int(score), 'info': '没有提示信息'}
                        else:
                            case = {'desc': i, 'score': 0, 'info': '出错了,请联系题目作者调试题目'}
                    except:
                        case = {'desc': i, 'score': 0, 'info': '题目有错'}
                    i += 1
                    cases.append(case)
    except:
        cases = []
    return cases


def get_totalScore(test_cases):
    """
    根据测试点信息，求得题目的总分
    :param test_cases: 测试点信息列表
    :return: 总分
    """
    total_score = 0
    for score in test_cases:
        total_score += int(score['score'])
    return total_score


@permission_required('judge.add_problem')
def verify_file(request):
    """
    验证上传的文件是否符合规范
    :param request: 上传文件请求
    :return: 以json格式返回文件验证信息
    """
    file = request.FILES['file_upload']
    count = in_count = out_count = 0
    random_name = ''.join(random.sample(string.digits + string.ascii_letters * 10, 8))  # 生成随机字符串作为文件名保存文件，防止相同文件名冲突
    tempdir = os.path.join('/tmp', random_name)
    os.mkdir(tempdir)
    filename = os.path.join(tempdir, file.name)
    with open(filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    un_zip(filename)

    r3 = re.compile('\d+ \d+ #.*#')
    r2 = re.compile('^\d+ \d+$')
    r22 = re.compile('^\d+ #.*#$')
    r1 = re.compile('^\d$')

    try:
        score_filename = filename + '_files/' + "scores.txt"
        for root, dirs, files in os.walk(filename + '_files/'):  # 去除文件BOM头
            for f in files:
                if not f.startswith('._'):
                    remove_bom(filename + '_files/' + f)
        with open(score_filename, 'rb') as f:
            data = f.read().decode('utf-8')
            lines = data.splitlines()
            for line in lines:
                if line:
                    if not (r3.match(line) or r2.match(line) or r22.match(line) or r1.match(line)):
                        shutil.rmtree(tempdir)
                        return HttpResponse(
                            json.dumps({'result': 0, 'info': 'scores.txt文件不符合规范，请注意对应测试用例名称，分值，描述之间以空格分割'}))
                count += 1
    except Exception as e:
        shutil.rmtree(tempdir)
        return HttpResponse(
            json.dumps({'result': 0, 'info': 'scores.txt文件不符合规范，请注意文件最后不要多余空行，并且文件均为UTF8编码' + e.__str__()}))
    for parentdir, dirname, filenames in os.walk(filename + '_files/'):
        for filename in filenames:
            if not filename.startswith("._"):
                if os.path.splitext(filename)[1] == '.in':
                    in_count += 1
                elif os.path.splitext(filename)[1] == '.out':
                    out_count += 1
    if in_count != count:
        shutil.rmtree(tempdir)
        return HttpResponse(json.dumps({'result': 0, 'info': '.in文件数量与scores.txt中的评分项目不符'}))
    if out_count != count:
        shutil.rmtree(tempdir)
        return HttpResponse(json.dumps({'result': 0, 'info': '.out文件数量与scores.txt中的评分项目不符'}))
    return HttpResponse(json.dumps({"result": 1, 'info': random_name, 'filename': file.name}))


def un_zip(file_name):
    """
    解压zip文件到当前目录，并生成"file_name_files"文件夹保存解压的数据
    :param file_name: 文件名
    :return: 无
    """
    zip_file = zipfile.ZipFile(file_name)
    os.mkdir(file_name + "_files")
    for names in zip_file.namelist():
        zip_file.extract(names, file_name + "_files/")
    zip_file.close()


"""
Remove BOM(Byte Order Marker) from utf-8 files.
"""


def init_options():
    parser = argparse.ArgumentParser(description='Remove BOM(Byte Order Marker) from utf-8 files.')
    parser.add_argument('path', type=str, help='path of the target folder')
    parser.add_argument('--type', dest='type', help='file type')
    return parser.parse_args()


def remove_bom(filepath):
    """
    移除记事本保存UTF8编码文件的BOM头
    :param filepath: 文件路径
    :return: 无
    """
    with open(filepath, 'r+b') as fp:
        chunk = fp.read(BUFSIZE)
        if chunk.startswith(codecs.BOM_UTF8):
            i = 0
            chunk = chunk[BOMLEN:]
            while chunk:
                fp.seek(i)
                fp.write(chunk)
                i += len(chunk)
                fp.seek(BOMLEN, os.SEEK_CUR)
                chunk = fp.read(BUFSIZE)
            fp.seek(-BOMLEN, os.SEEK_CUR)
            fp.truncate()
            print('Converted: ' + filepath)
        else:
            print(filepath + " file_encoding is utf8 without BOM.")
