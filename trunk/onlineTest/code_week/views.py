from django.shortcuts import render
from .models import CodeWeekClass, ProblemCategory, CodeWeekClassStudent
from .forms import *
import datetime
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from auth_system.models import MyUser, Group
from django.http import HttpResponse,StreamingHttpResponse
import os, cgi, json
from django.views.generic.detail import DetailView
from django.utils.datastructures import MultiValueDictKeyError
from django.apps import apps

@login_required
def course_list_for_student(request):
    nowtime = datetime.datetime.now()         #获取当前时间用来判断有关学生的课程是否在进行
    nowCourses = CodeWeekClass.objects.filter(
        students=request.user).filter(  #过滤获取学生正在进行的课程
        begin_time__lte=nowtime).filter(
        end_time__gte=nowtime
    )
    previousCourses = CodeWeekClass.objects.filter( #过滤获取已经结束的课程
        students=request.user).filter(
        end_time__lt=nowtime
    )
    futureCourses = CodeWeekClass.objects.filter(   #过滤获取还未开始的课程
        students=request.user).filter(
        begin_time__gt=nowtime
    )
    return render(request, 'code_week/course_list.html',
                  {'nowCourses' : nowCourses, 'previousCourses' : previousCourses, 'futureCourses' : futureCourses, 'position': 'code_week_list'})

@permission_required('code_week.add_codeweekclass')
def course_list_for_teacher(request):
    nowtime = datetime.datetime.now()  # 获取当前时间用来判断有关老师的课程是否在进行
    nowCourses = CodeWeekClass.objects.filter(
        teacher=request.user).filter( # 过滤获取老师正在进行的课程
        begin_time__lte=nowtime).filter(
        end_time__gte=nowtime
    )
    previousCourses = CodeWeekClass.objects.filter(  # 过滤获取已经结束的课程
        teacher=request.user).filter(
        end_time__lt=nowtime)
    futureCourses = CodeWeekClass.objects.filter(    # 过滤获取还未开始的课程
        teacher=request.user).filter(
        begin_time__gt=nowtime)
    return render(request, 'code_week/courses.html',
                  {'nowCourses': nowCourses, 'previousCourses': previousCourses, 'futureCourses': futureCourses, 'position': 'code_week_teacher_course_list'})

#重点是学生的添加，这里的策略是通过学号添加，可以是学号范围，也可以是单个学号，这里设定所有合法的学号长度都是为9的
@permission_required('code_week.add_codeweekclass')
def add_course(request):
    if request.method == 'POST':
        form = AddCodeWeekForm(request.POST)
        if form.is_valid():
            print("form correct")
            print(form.cleaned_data['course_name'])
            print(form.cleaned_data['begin_time'])
            print(form.cleaned_data['end_time'])
            print(form.cleaned_data['problems'])
            begin_time = form.cleaned_data['begin_time']
            end_time = form.cleaned_data['end_time']
            if end_time <= begin_time:
                return HttpResponse("时间不对")
            newCourse = CodeWeekClass(name=form.cleaned_data['course_name'],
                                      teacher=request.user,
                                      begin_time=begin_time,
                                      end_time=end_time,
                                      numberEachGroup=form.cleaned_data['maxnumber'])
            newCourse.save()
            # 添加题目
            if form.cleaned_data['problems']:
                ids = form.cleaned_data['problems'].split(',')
                try:
                    for pk in ids:
                        newCourse.problems.add(pk)
                except:
                    return HttpResponse(0)
            # 添加学生
            for stu_detail in request.POST['students'].splitlines():
                # print(line)
                if len(stu_detail.split()) > 1:
                    id_num, username = stu_detail.split()[0], stu_detail.split()[1]
                    try:
                        student = MyUser.objects.get(id_num=id_num)
                    except:
                        student = MyUser(id_num=id_num, email=id_num + '@njupt.edu.cn', username=username)
                        student.set_password(id_num)
                        student.save()
                        student.groups.add(Group.objects.get(name='学生'))
                #newCourse.students.add(student)
                newCourseStudent = CodeWeekClassStudent(codeWeekClass=newCourse, student=student)
                newCourseStudent.save()
            return HttpResponse(1)
        else:
            print(form.errors)
    else:
        form = AddCodeWeekForm()
        categorys = ProblemCategory.objects.all()
        return render(request, 'code_week/add_course.html', {'form': form, 'categorys': categorys})

#教师查看课程主页
@permission_required('code_week.change_codeweekclass')
def view_course(request, courseId):
    course = CodeWeekClass.objects.filter(id=courseId)
    if course.count() == 0:
        return render(request, 'warning.html', {'info' : '查无此课'})
    elif course[0].teacher != request.user:
        return render(request, 'warning.html', {'info': '查无此课'})
    else:
        students = course[0].students.all()
        problems = course[0].problems.all()
        return render(request, 'code_week\course_detail.html', {'course' : course[0], 'students' : students, 'problems':problems})

#学生查看课程主页
@login_required()
def student_view_course(request, courseId):
    course = CodeWeekClass.objects.filter(id=courseId)
    if course.count() == 0:
        return render(request, 'warning.html', {'info' : '查无此课'})
    elif request.user in course[0].students.all(): # 请求的用户在课程学生列表中
        return render(request, 'code_week\student_course_detail.html', {'course' : course[0]})
    else:
        return render(request, 'warning.html', {'info': '查无此课'})

# 用户提交文件名，把文件名修改为提交的id
def newFileName(fileId):
    filename = os.path.join('C:/Users/张柯/code/upload/', str(fileId))
    return filename

#增加程序设计题
@permission_required('code_week.add_shejiproblem')
def add_sheji(request):
    if request.method == 'POST':  # 当提交表单时
        form = ShejiAddForm(request.POST,request.FILES)  # form 包含提交的数据
        print(form.errors)
        if form.is_valid():  # 如果提交的数据合法
            f = request.FILES.get('headImg')
            problem = form.save(user=request.user)  # 保存题目

            filename = newFileName(problem.problem_id)
            fobj = open(filename,'wb')
            for chrunk in f.chunks():#可以设置分块上传
                fobj.write(chrunk)
            fobj.close()
            return redirect(reverse("sheji_detail", args=[problem.problem_id]))
    else:  # 当正常访问时
        form = ShejiAddForm()
    return render(request, 'code_week/sheji_problem_add.html', {'form': form, 'title': '新建程序设计题'})

#删除程序设计题(未完成)
@permission_required("code_week.delete_shejiproblem")
def delete_sheji(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ids[]')
        try:
            for pk in ids:
                ShejiProblem.objects.filter(pk=pk).filter(creator=request.user).delete()
        except:
            return HttpResponse(0)
        return HttpResponse(1)
    else:
        return HttpResponse(0)

#程序设计题详细视图(未完成)
class ShejiProblemDetailView(DetailView):
    model = ShejiProblem
    template_name = 'code_week/sheji_problem_detail.html'
    context_object_name = 'problem'
    def get_context_data(self, **kwargs):
            context = super( ShejiProblemDetailView, self).get_context_data(**kwargs)
            context['title'] = '程序设计题“' + self.object.title + '”的详细信息'
            return context

#更新程序设计题
@permission_required('code_week.change_shejiproblem')
def update_sheji(request, id):
    problem = get_object_or_404(ShejiProblem, pk=id)
    if problem.creator != request.user:
        return render(request, 'warning.html', {'info' : "您无法修改不是您创建的题目"})
    initial = {'title': problem.title,
               'editorText':problem.editorText,
               'category':problem.category,
               }  # 生成表单的初始化数据
    if request.method == "POST":  # 当提交表单时
        form = ShejiUpdateForm(request.POST,request.FILES)
        if form.is_valid():
            form.save(user=request.user, problemid=id)
            f = request.FILES.get('headImg')
            if f: # 重新上传了文件
                fobj = open(newFileName(id), 'wb')
                for chrunk in f.chunks():
                    fobj.write(chrunk)
                fobj.close()
            return redirect(reverse("sheji_detail", args=[id]))
    return render(request, 'code_week/sheji_problem_update.html', {'form': ShejiUpdateForm(initial=initial), 'problem': problem})

# 程序设计题列表
@login_required()
def list_sheji(request):
    categorys = ProblemCategory.objects.all()
    return render(request, 'code_week/sheji_problem_list.html', context={'categorys': categorys, 'title': '程序设计题题库', 'position': 'sheji_list'})

@login_required()
def get_json_sheji(request):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    category = int(request.GET['category'])

    if category != 0:
        problems = ShejiProblem.objects.filter(category=category)
    else:
        problems = ShejiProblem.objects
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
        title = cgi.escape(problem.title)
        recode = {'pk': problem.pk, 'title': title, 'category': str(problem.category),
                  'update_date': problem.update_date.strftime('%Y-%m-%d %H:%M:%S'), 'creator': str(problem.creator),
                  'id': problem.pk}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))

#用于学生查看自己课程中的所有题目
@login_required()
def get_problem_student(request, id):
    json_data = {}
    recodes = []
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    course = get_object_or_404(CodeWeekClass, id=id)
    json_data['total'] = course.problems.all().count()
    problems = course.problems.all()
    for problem in problems.all().order_by('pk')[offset:offset + limit]:
        title = cgi.escape(problem.title)
        outline = ""
        for aline in problem.editorText.splitlines():
            outline += aline
            outline += '<br/>'
        recode = {'pk': problem.pk, 'title': title, 'category': str(problem.category),
                 'outline' : outline,
                  'id': problem.pk}
        recodes.append(recode)
    json_data['rows'] = recodes
    return HttpResponse(json.dumps(json_data))


def encodeFilename(filename):
    """
    :param filename:
    :return: 将中文的文件名编码成为Content-Disposition中能够被浏览器识别的UTF-8格式的文件名
    例如文件名为"张柯.doc",需要设置为'''attachment;filename*=UTF-8''%e5%bc%a0%e6%9f%af.doc'''
    然而str.encode("utf-8")返回的结果为b'\xe5\xbc\xa0\xe6\x9f\xaf.doc'需要转换一下
    这个函数就是将含有中文的文件名转换一下
    """
    originStr = str(filename.encode("utf-8"))
    print(originStr)
    originStr = originStr.replace("\\x","%")
    print(originStr)
    returnstr = originStr[2:len(originStr)-1]
    return returnstr

# 实现描述文件的下载功能
@login_required()
def download(request, fileId):
    files = ShejiProblem.objects.filter(problem_id=fileId)
    if files: #能够搜索到
        file = files[0]
        filename = newFileName(fileId)

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, 'rb') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(filename))
        response['Content-Type'] = files[0].content_type
        response['Content-Disposition'] = '''attachment;filename*= UTF-8''{0}'''.format(encodeFilename(files[0].filename))
        return response
    else:
        return render(request, 'warning.html' ,{'info' : '没有此文件'})
