import os.path, uuid
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db import connection
from django.db.models import Count
from sign.models import Event, Sign, Leave, Record
from auth_system.models import MyUser
from work.models import BanJi
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from onlineTest.settings import BASE_DIR


def teacher_index(request):
    user = request.user

    if request.method == 'GET' and user.is_admin:    

        cursor = connection.cursor()
        classesSql = 'select id, name\
            from work_banji \
            where teacher_id = %d' % user.id
        cursor.execute(classesSql)
        classes = list(map(lambda x: dict(zip(['banjiId', 'name'], x)), cursor.fetchall()))
        
        signList = Event.objects.all().filter(teacher_id = user.id).prefetch_related('banji').values(
            'id', 'has_signed_count', 'all_student_count', 'created_time', 'started_time', 'closed_time', 'banji__name'
        )

        return render(request, "sign_teacher_index.html", {
            'data': signList,
            'classes': classes
        })


@csrf_exempt
def create(request):
    user = request.user

    if request.method == 'POST' and user.is_admin:   #judge HTTP method and user identity

        banjiId = int(request.POST.get('banjiId'))
        timeNow = datetime.now()

        Event.objects.create(
            position = request.POST.get('position'),    #点名发起的位置，以此来判断学生是否在指定范围内签到
            has_signed_count = 0,
            all_student_count = BanJi.objects.get(id = banjiId).students.count(),
            started_time = request.POST.get('startedTime', timeNow.strftime('%Y-%m-%d %H:%M:%S')),     #点名开始的时间，可自定义
            closed_time = request.POST.get('closedTime', (timeNow + timedelta(minutes = 10)).strftime('%Y-%m-%d %H:%M:%S')),    #点名结束的时间，默认10min的点名期限
            banji_id = banjiId,
            teacher_id = user.id
        )
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errMsg': 'Permission denied'})


@csrf_exempt
def delete(request, eventId):
    Event.objects.filter(id = int(eventId)).delete()
    return JsonResponse({'success': True})


def detail(request, eventId):
    event = Event.objects.get(id = int(eventId))

    cursor = connection.cursor()

    sql = '\
        SELECT s.id, u.username, s.type_of, s.is_checked, s.created_time, sl.cause, sl.path\
            FROM work_banji_students AS bj_stu\
                INNER JOIN auth_system_myuser AS u\
                ON u.id = bj_stu.myuser_id\
                LEFT JOIN sign_sign AS s\
                ON u.id = s.user_id and bj_stu.banji_id = (\
                    SELECT banji_id FROM sign_event WHERE id = %d\
                )\
                LEFT JOIN sign_leave AS sl\
                ON s.id = sl.sign_id\
                WHERE bj_stu.banji_id = %d' % ( int(eventId), event.banji_id )

    cursor.execute(sql)
    studentsList = list(map(lambda x: dict(zip(['id', 'username', 'type_of', 'is_checked', 'created_time', 'cause', 'path'], x)), cursor.fetchall()))

    return render(request, "sign_detail.html", {
        'data': studentsList,
        'eventId': eventId
    })


def student_index(request):
    userId = request.user.id
    cursor = connection.cursor()

    ongoingSQL = '\
        select e.id, tmp.name, e.position, e.started_time, e.closed_time\
        from sign_event AS e\
        join \
        (\
            select bj_mid.banji_id, bj.name\
            from work_banji_students AS bj_mid\
            join work_banji AS bj\
            on bj_mid.banji_id = bj.id and bj_mid.myuser_id = %d\
            where now() between bj.start_time and bj.end_time\
        ) AS tmp\
        on e.banji_id = tmp.banji_id\
        where now() between e.started_time and e.closed_time\
    ' % userId
    cursor.execute(ongoingSQL)
    onGoing = list(map(lambda x: dict(zip(['id', 'name', 'position', 'startTime', 'closedTime'], x)), cursor.fetchall()))
    onGoing = onGoing[0] if onGoing else []

    checkedSQL = '\
        select bj.name, s.created_time\
        from sign_sign AS s\
        join sign_event AS e\
        on s.event_id = e.id\
        join work_banji AS bj\
        on bj.id = e.banji_id\
        where user_id = %d\
    ' % userId
    cursor.execute(checkedSQL)
    checked = list(map(lambda x: dict(zip(['name', 'createdTime'], x)) ,cursor.fetchall()))

    return render(request, "sign_student_index.html", {
        'onGoing': onGoing,
        'checked': checked
    })


# 学生主动签到的动作
@csrf_exempt
def checkout(request, eventId):
    eventId = int(eventId)
    try:
        ip =  request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        ip = request.META['REMOTE_ADDR']

    if Sign.objects.filter(event_id = eventId, user_id = request.user.id):
        return JsonResponse({'success': False, 'errMsg': 'You have already sign'})

    if Record.objects.filter(event_id = eventId, address = ip):
        return JsonResponse({'success': False, 'errMsg': '签到无效，同一设备不可重复签到'})

    event = Event.objects.get(id = eventId)
    event.has_signed_count = event.has_signed_count + 1
    event.save()

    Sign.objects.create(
        event_id = eventId,
        user_id = request.user.id,
        type_of = 0,
        is_checked = 1
    )

    Record.objects.create(
        event_id = eventId,
        address = ip
    )

    return JsonResponse({'success': True})



#老师手动输入学号帮助学生签到
@csrf_exempt
def supplement(request, eventId):
    eventId = int(eventId)
    studentId = request.POST.get('studentId')
    
    try:
        userId = MyUser.objects.get(id_num = studentId).id        
    except:
        return JsonResponse({'success': False, 'code': 404, 'errMsg': 'can not find user by studentId'})

    Sign.objects.create(
        event_id = eventId,
        user_id = userId,
        type_of = 0,
        is_checked = 1
    )

    event = Event.objects.get(id = eventId)
    event.has_signed_count = event.has_signed_count + 1
    event.save()

    return JsonResponse({'success': True})


@csrf_exempt
def leave(request, eventId):
    userId = request.user.id
    eventId = int(eventId)

    if Sign.objects.filter(event_id = eventId, user_id = userId):
        return JsonResponse({'success': False, 'errMsg': 'You have already sign'})

    fileObj = request.FILES.get('leaveAsk')
    #检测文件后缀名和 MINE 格式
    #暂时还不知道 怎么判断上传文件的 MINE 类型，目前只根据后缀检查一下
    if os.path.splitext(fileObj.name)[1].lower() not in ('.jpg', '.jpeg', '.png'):
        return JsonResponse({'success': False, 'state': 0, 'msg': 'upload file can only be .jpg .jpeg .png'})

    date = datetime.now().strftime('%Y/%m/%d/').split('/')
    pathdir = os.path.join(BASE_DIR, 'static', 'pic', date[0], date[1], date[2])
    if not os.path.exists(pathdir):
        os.makedirs(pathdir)
    
    fileName = str(uuid.uuid1())
    f = open(os.path.join(pathdir, fileName), 'wb')
    for chunk in fileObj.chunks():
        f.write(chunk)
    f.close()

    signObj = Sign(event_id = eventId, user_id = userId, type_of = 1, is_checked = 0)
    signObj.save()

    Leave.objects.create(
        sign_id = signObj.id,
        path = os.path.join('pic', date[0], date[1], date[2], fileName),
        cause = request.POST.get('cause')
    )

    return JsonResponse({'success': True, 'state': 1, 'path': os.path.splitext(fileObj.name)})


@csrf_exempt
def accept (request, signId):
    sign = Sign.objects.get(id = signId)
    sign.is_checked = 1

    event = Event.objects.get(id = sign.event_id)
    event.has_signed_count = event.has_signed_count + 1
    
    event.save()
    sign.save()

    cursor = connection.cursor()
    sql = 'SELECT path FROM sign_leave WHERE sign_id = %d' % int(signId)
    cursor.execute(sql)
    lPath = cursor.fetchall()
    os.remove(BASE_DIR + '/static/' + lPath[0][0])

    sql = 'DELETE FROM sign_leave WHERE sign_id = %d' % int(signId)
    cursor.execute(sql)

    return JsonResponse({'success': True})


@csrf_exempt
def decline (request, signId):

    cursor = connection.cursor()
    sql = 'DELETE FROM sign_sign WHERE id = %d' % int(signId)
    cursor.execute(sql)
    
    sql = 'SELECT path FROM sign_leave WHERE sign_id = %d' % int(signId)
    cursor.execute(sql)
    lPath = cursor.fetchall()
    os.remove(BASE_DIR + '/static/' + lPath[0][0])

    sql = 'DELETE FROM sign_leave WHERE sign_id = %d' % int(signId)
    cursor.execute(sql)

    return JsonResponse({'success': True})


def setAddress (request, signId, userId, address):
    pass