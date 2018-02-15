from channels import Channel, Group
from channels.sessions import channel_session
from channels.auth import channel_session_user, channel_session_user_from_http
from .models import *
import json, pdb
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import IPython

def sendMsgToStudent(message, text):
    # 将消息发给学生一个人，一般用于命令的反馈
    Group(str(message.user.id), channel_layer=message.channel_layer).send({'text': json.dumps(text)})

def sendMsgToClass(courseId, message, text):
    # 将消息发给一个班级的人，一般用于命令处理成功的广播消息
    Group('codeweekStudent-' + courseId, channel_layer=message.channel_layer).send(
        {'text': json.dumps(text)})

@channel_session_user_from_http
def ws_connect_teacher_detail(message, courseId):
    """
    :param message: websocket的消息
    :param courseId: 通过router正则匹配到的课程id
    如果通过数据库查找判断了连接的用户是这个课程的教师，会允许这个连接
    将这个wb放到channel的一个组内来实时发送消息
    """
    #核查是否是该用户的课程
    course = None
    try:
        course = CodeWeekClass.objects.get(id=courseId) # 查询id为courseId的程序设计课
    except ObjectDoesNotExist:
        message.reply_channel.send({"accept": False})   # 断开这个wb连接
        return
    if course and course.teacher == message.user:
        message.reply_channel.send({"accept": True})    # 允许连接
        #将连接加入到Group中
        Group('codeweekTeacher-'+courseId, channel_layer=message.channel_layer).add(message.reply_channel)
    else:
        message.reply_channel.send({"accept": False})

@channel_session_user
def ws_disconnect_teacher_detail(message, courseId):
    """
    :param message: websocket的消息
    :param courseId: 通过router正则匹配到的课程id
    接收wb的断开连接消息，将wb从channel的老师课程组中移除
    """
    course = None
    try:
        course = CodeWeekClass.objects.get(id=courseId)
    except ObjectDoesNotExist:
        return
    if course.teacher == message.user:
        # 将连接从Group中移除
        Group('codeweekTeacher-' + courseId, channel_layer=message.channel_layer).discard(message.reply_channel)
    else:
        pass

@channel_session_user_from_http
def ws_connect_student_detail(message, courseId):
    """
    :param message: websocket的消息
    :param courseId: 通过router正则匹配到的课程id
    判断这个wb连接的用户是否是这个课程中的学生
    如果是，加入到这个课程的学生组中用来实时发送有关学生建组，加入的操作
    """
    #核查用户是否在这个课的名单中
    # course = None
    # try:
    #     course = CodeWeekClass.objects.filter(id=courseId)
    # except ObjectDoesNotExist:
    #     return
    # if course:
    if CodeWeekClassStudent.objects.filter(codeWeekClass=courseId, student=message.user).exists():
        message.reply_channel.send({"accept": True})
        # 加入到这个课程的频道中
        Group('codeweekStudent-' + courseId, channel_layer=message.channel_layer).add(message.reply_channel)
        # 加入到自己的专属频道
        Group(str(message.user.id), channel_layer=message.channel_layer).add(message.reply_channel)
    else:
        message.reply_channel.send({"accept": False})
    # if course.count() != 0:
    #     thiscourse = course[0]
    #     if thiscourse.students.all().filter(codeweekclassstudent__student=message.user).count() != 0:
    #         message.reply_channel.send({"accept": True})
    #         #加入到这个课程的频道中
    #         Group('codeweekStudent-'+courseId, channel_layer=message.channel_layer).add(message.reply_channel)
    #         #加入到自己的专属频道
    #         Group(str(message.user.id), channel_layer=message.channel_layer).add(message.reply_channel)
    # message.reply_channel.send({"accept": False})

@channel_session_user
def ws_receive_student_detail(message, courseId):
    """
    :param message:websocket的消息
    :param courseId: 通过router正则匹配到的课程id
    处理学生发送的有关建组，加入组的操作
    把每条消息都保存下来，并且对每条成功操作的消息以班级分类标号
    每个班级的信息都会维护一个最大编号
    这个编号用来给前端确保数据完整，如果中间编号丢失，前端会主动发请求获取丢失的
    """
    # 核查用户是否在这个课的名单中
    # course = None
    # try:
    #     course = CodeWeekClass.objects.filter(id=courseId)
    # except ObjectDoesNotExist:
    #     return
    # if course:
    student = None
    try:
        student = CodeWeekClassStudent.objects.get(codeWeekClass=courseId, student=message.user)
    except ObjectDoesNotExist:
        return

    if student:
        #开始处理消息
        msg = ""
        action = ""
        try:
            msg = json.loads(message['text'])
            action = msg['action']
        except:
            return
        if action == 'c':   # 创建新分组（成为组长）
            #检查一下是否已经加入了分组
            if student.group: # 已经加入组了
                if student.isLeader: # 还是组长
                    result = {'msg': 'fail', 'info': '您已经是组长了'}
                    sendMsgToStudent(message, result)
                else:
                    result = {'msg': 'fail', 'info': '您已经加入一个组了'}
                    sendMsgToStudent(message, result)
                return
            else: #还没有在组中
                result = None
                try:
                    with transaction.atomic():
                        # 下面创建小组并且存储操作
                        # 创建小组需要create，将学生的group设为新建的小组，将学生isLeader属性改为True
                        # 存储学生的修改
                        # 增加课程的计数值
                        # 存储课程的修改
                        # 存储这次修改的操作
                        courses = CodeWeekClass.objects.select_for_update().filter(id=courseId)  # 显式要求update锁，在事务结束时会自动释放
                        course = courses[0]
                        newGroup = CodeWeekClassGroup.objects.create(cwclass=course)
                        student.group = newGroup
                        student.isLeader = True
                        student.save()
                        course.counter += 1
                        course.save()
                        result = {'action': 'c', 'groupId': newGroup.id, 'leader': student.get_full_name(), 'operationId': course.counter}
                        ClassOperation.objects.create(cwclass=course, operation_id=(course.counter),
                                                      operation=json.dumps(result))
                except:
                    #发生异常了，事务回滚，建立组的操作并没有完成
                    sendMsgToStudent(message, {'msg': 'fail'})
                    return
                # msg = {'action': 'c', 'id': newGroup.id, 'leader': student.get_full_name()}
                sendMsgToStudent(message, {'msg': 'success'})
                sendMsgToClass(courseId, message, result)

        elif action == 'j':  # 加入分组
            #获取分组号
            groupid = 0
            try:
                groupid = json.loads(message['text'])['id']
            except:
                return
            #检查一下是否已经加入了分组
            student = None
            try:
                student = CodeWeekClassStudent.objects.get(codeWeekClass=courseId, student=message.user)
            except ObjectDoesNotExist:
                return
            if student.group: # 已经加入组了
                if student.isLeader: # 还是组长
                    result = {'msg': 'fail', 'info': '您已经是组长了'}
                    sendMsgToStudent(message, result)
                else:
                    result = {'msg': 'fail', 'info': '您已经加入一个组了'}
                    sendMsgToStudent(message, result)
                return
            else: #还没有在组中
                #加入分组
                group = ""
                try:
                    group = CodeWeekClassGroup.objects.get(id=groupid)
                except: #组不存在
                    sendMsgToStudent(message, {'msg': 'fail', 'info': '组不存在'})
                    return
                if group.Group_member.count() >= CodeWeekClass.objects.get(id=courseId).numberEachGroup: #人已经满了
                    result = {'msg': 'fail', 'info': '组中人已经满了'}
                    sendMsgToStudent(message, result)
                else: # 加入组并且保存这个成功的操作
                    result = None
                    try:
                        with transaction.atomic():
                            # 加入分组的步骤
                            # 将学生的group设为要加入的组，将学生的isLeader改为False
                            # 存储学生
                            # 自增课程的计数值并存储
                            # 存储这次操作
                            courses = CodeWeekClass.objects.select_for_update().filter(
                                id=courseId)  # 显式要求update锁，在事务结束时会自动释放
                            course = courses[0]
                            student.group = group
                            student.isLeader = False
                            student.save()
                            # 存储这次操作
                            course.counter += 1
                            course.save()
                            result = {'action': 'j', 'student': student.get_full_name(), 'groupId': groupid,
                                   'operationId': course.counter}
                            ClassOperation.objects.create(cwclass=course, operation_id=(course.counter),
                                                          operation=json.dumps(result))
                    except:
                        sendMsgToStudent(message, {'msg': 'fail'})
                        return
                    sendMsgToStudent(message, {'msg': 'success'})
                    sendMsgToClass(courseId, message, result)

        elif action == 'd':  # 删除分组
            # 检查是否是组长
            student = None
            try:
                student = CodeWeekClassStudent.objects.get(codeWeekClass=courseId, student=message.user)
            except ObjectDoesNotExist:
                return

            if student.group:
                if not student.isLeader: # 不是组长
                    result = {'msg': 'fail', 'info': '您不是组长'}
                    sendMsgToStudent(message, result)
                    return
                if student.group.Group_member.count() != 1:  #除了自己还有别人，不能删除
                    result = {'msg': 'fail', 'info': '组内有其他人'}
                    sendMsgToStudent(message, result)
                    return
                else: #可以删除
                    groupid = None
                    result = None
                    try:
                        with transaction.atomic():
                            # 删除分组的操作
                            # 首先记录下groupid，在后面的记录操作要用到
                            # 将group的using属性设为False，表示这个组不用了
                            # 将学生的group属性设为None，isLeader设为False，存储
                            # 自增课程的计数值，存储
                            # 存储这次操作
                            courses = CodeWeekClass.objects.select_for_update().filter(
                                id=courseId)  # 显式要求update锁，在事务结束时会自动释放
                            course = courses[0]
                            groupid = student.group.id
                            student.group.using = False # 将组标记为不在使用
                            student.group.save()
                            student.group = None
                            student.isLeader = False
                            student.save()
                            course.counter += 1
                            course.save()
                            result = {'action': 'd', 'student': student.get_full_name(), 'groupId': groupid,
                                   'operationId': course.counter}
                            ClassOperation.objects.create(cwclass=course, operation_id=(course.counter),
                                                          operation=json.dumps(result))
                    except:
                        sendMsgToStudent(message, {'msg': 'fail'})
                        return
                    sendMsgToStudent(message, {'msg': 'success'})
                    sendMsgToClass(courseId, message, result)
            else:
                result = {'msg': 'fail', 'info': '您还没有创建组'}
                sendMsgToStudent(message, result)

        elif action == 'r':   #移除组员
            student = None
            try:
                student = CodeWeekClassStudent.objects.get(codeWeekClass=courseId, student=message.user)
            except ObjectDoesNotExist:
                return
            if student.group:
                if not student.isLeader: # 不是组长
                    result = {'msg': 'fail', 'info': '您不是组长'}
                    sendMsgToStudent(message, result)
                    return
                else:
                    toRemove = None
                    try:
                        toRemove = msg['name']
                    except:
                        return
                    result = None
                    try:
                        with transaction.atomic():
                            # 移除组员的步骤
                            # 遍历自己的小组成员看全名（学号+名字）是否匹配
                            # 匹配到将组员的group属性设为None，存储
                            # 将课程的操作计数值增加，存储
                            # 记录下这次操作
                            for member in student.group.Group_member.all():
                                if toRemove == member.get_full_name():
                                    courses = CodeWeekClass.objects.select_for_update().filter(
                                        id=courseId)  # 显式要求update锁，在事务结束时会自动释放
                                    course = courses[0]
                                    member.group = None
                                    member.save()
                                    # 存储这次操作
                                    course.counter += 1
                                    course.save()
                                    result = {'action': 'r', 'member': member.get_full_name(), 'groupId': student.group.id,
                                           'operationId': course.counter}
                                    ClassOperation.objects.create(cwclass=course, operation_id=(course.counter),
                                                                  operation=json.dumps(result))
                                    break
                    except:
                        result = {'msg': 'fail'}
                        sendMsgToStudent(message, result)
                        return
                    sendMsgToStudent(message, {'msg':'success'})
                    sendMsgToClass(courseId, message, result)

            else: # 都没有小组
                result = {'msg' : 'fail', 'info': '您还没有加入小组'}
                sendMsgToStudent(message, result)
                return

        #Group('codeweekStudent-' + courseId, channel_layer=message.channel_layer).send({'text': message['text']})

@channel_session_user
def ws_disconnect_student_detail(message, courseId):
    # 核查用户是否在这个课的名单中
    course = CodeWeekClass.objects.filter(id=courseId)
    if course.count() != 0:
        thiscourse = course[0]
        if thiscourse.students.all().filter(codeweekclassstudent__student=message.user).count() != 0:
            print("student out")
            Group('codeweekStudent-' + courseId, channel_layer=message.channel_layer).discard(message.reply_channel)
            Group(str(message.user.id), channel_layer=message.channel_layer).discard(message.reply_channel)
    else:
        pass