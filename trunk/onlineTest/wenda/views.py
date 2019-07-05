# -*- conding:utf-8 -*-

from django.shortcuts import render, render_to_response, HttpResponse	
from django.contrib.auth.decorators import permission_required, login_required
from wenda.models import *
from auth_system.models import MyUser
from django.contrib.auth.models import Group
from judge.models import ClassName
from django.http import HttpResponseRedirect
import datetime
import json
import os

from django.conf import settings

# USER_FILE_DIR
def getImg(request,path):
    # print("path:"+path)
    path = path.split('/')
    file_path = os.path.join(settings.USER_FILE_DIR, "media", path[0], path[1])
    with open(file_path,"rb") as f:
        img = f.read()
    img_type = r'image/' + path[1].split('.')[-1]
    # print(img_type)
    return HttpResponse(img,content_type = img_type)

def getRole(user):
    # n：表示未登录用户 a：超级管理员 t：教师 s：学生

    role = 'n'
    if user.is_superuser:
        role =  'a'
    elif user.isTeacher:
        role =  't'
    else:
        role =  's'
    return role

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

from message.views import createMsg
from message.models import Message

# Create your views here.

# @login_required()
# def index(request):
# 	return render(request, 'wenda/index.html', {'SITE_NAME': '程序设计类课程作业平台'})


# 每次加载问题的个数
LOAD_Q_NUM = 6

# 首页处理函数
# 取出每个问题的如下信息
# id:问题id, ques:问题, update_date:提问日期,tag:所属类别, 
# asker_id：提问者id, praisenum：点赞数, description：问题附加描述,
# username：提问者姓名,answernum：答案数目
@login_required()
def index(request):
    question = Question.objects.all().order_by('-id').values('id', 'ques', 'update_date',
                                    'tag', 'asker_id', 'praisenum', 'description')[0:LOAD_Q_NUM]
    for q in question:
        user = MyUser.objects.get(id=q['asker_id'])
        answernum = Answer.objects.filter(question=q['id']).count()
        answernum += RecommendAns.objects.filter(qid=q['id']).count()
        idnum = user.id_num
        if idnum:
            username = idnum + ' ' + user.username
        else:
            username = user.username
        q['username'] = username
        q['answernum'] = answernum
        
    mnum = Message.objects.filter(rid = request.user.id, isread=False).count()
    request.session['mnum'] = mnum

    response = render(request, 'wenda/index.html', {'question': question,'position':'wenda'})
    # 系统中所有问题的数目，用于异步加载问题时判断是否有必要发起请求
    Q_ALL = Question.objects.all().count()
    response.set_cookie("qnum", LOAD_Q_NUM)
    response.set_cookie("qall", Q_ALL)

    response.set_cookie("role", getRole(request.user))

    # response.set_cookie("qnum", LOAD_Q_NUM)
    # response.set_cookie("uname", request.user.username)
    return response

# 跳转提问页面
def ask(request):
	tag = ClassName.objects.all().values_list('name',flat=True)
	return render(request, 'wenda/ask.html',{'tag':tag,'position':'askqus'})

# 上传问题
@login_required()
def submitqus(request):
	ques = request.POST.get('question', None)
	tag = request.POST.get('tag', None)
	desc = request.POST.get('description', None)
	response = HttpResponse('0')
	if ques != None and tag != None:
		try:
			q = Question.objects.create(
			    asker=request.user, ques=ques, tag=tag, description=desc)
			invite_user = MyUser.objects.filter(groups__pk='1').order_by(
			    '?').values('id', 'username', 'id_num')[0:10]
			data = {}
			data['user'] = list(invite_user)
			data['qid'] = q.id
			_thread.start_new_thread(get_recommend_ans,(ques,q.id))
			response = HttpResponse(json.dumps(data), content_type="application/json")
		except Exception as e:
			# print(str(e))
			pass
	return response

# 回答问题(通过主页点开问题链接展开问题详情后可以选择回答)
def question_answer(request, qId):
    try:
        qId = int(qId)
        q = Question.objects.get(id=qId)
        ans = Answer.objects.filter(question_id=qId, replier=request.user)
        if ans.exists():
            answer = ans[0].answer
        else:
            answer = ''
        return render(request, 'wenda/question_answer.html', {'question': q, 'answer': answer})
    except Exception as e:
        # print(str(e))
        return render(request,'wenda/error.html',{'errorMsg':"跳转回答问题出错了..."})
        # return HttpResponse("跳转回答问题出错了...")


# createMsg(sid,rid,message,objId,objtype=0,messagetype=0)
# sid 消息发出者的id
# sname 消息发出者的姓名
# rid 消息接收者的id
# messagetype 消息类型
    # msgtype = (
    #     (0, u'系统消息'),
    #     (1, u'邀请消息'),
    #     (2, u'关注消息'),
    #     (3, u'回答问题消息'),
    #     (4, u'评论问题消息'),
    #     (5, u'更新答案消息'),
    # )
# message 消息内容
# objtype 消息面对的对象类型
    # objtypes = (
    #     (0, u'问题的id'),
    #     (1, u'答案的id'),
    # )

# 提交答案 返回 0表示答案为空 1表示成功 2表答案储存失败
@login_required()
def submitAnswer(request):
    role = Group.objects.get(user=request.user).id
    qid = request.POST.get('qid', '')
    response = HttpResponse(0)
    if qid != '' and role == 1:
        answer = request.POST.get('answer', '')
        if answer != '':
            try:
                ans = Answer.objects.filter(
                    question_id=qid, replier=request.user)
                qus = Question.objects.get(id=qid)
                if ans.exists():
                    ans.update(answer=answer)
                    idnum = request.user.id_num
                    if idnum:
                        sname = idnum + request.user.username
                    else:
                        sname = request.user.username
                    createMsg(sid=request.user.id, rid=qus.asker_id, message=qus.ques, objId=ans[0].id, messagetype=5)
                    # Message.objects.create(sid=request.user.id, sname=sname, messagetype=5, rid=qus.asker_id, message=qus.ques, objId=qid)
                else:
                    ans = Answer.objects.create(
                        question_id=qid, replier=request.user, answer=answer)
                    qus = Question.objects.get(id=qid)
                    # 问题回答者与提问者不能相同，即排除自问自答的情况
                    if qus.asker_id != request.user.id:
                        idnum = request.user.id_num
                        if idnum:
                            sname = idnum + request.user.username
                        else:
                            sname = request.user.username
                        createMsg(sid=request.user.id, rid=qus.asker_id, message=qus.ques, objId=ans.id, messagetype=3)
                        # Message.objects.create(sid=request.user.id, sname=sname, messagetype=3, rid=qus.asker_id, message=qus.ques, objId=qid)
                response =  HttpResponse(1)
            except Exception as e:
                # print(str(e))
                response =  HttpResponse(2)
   
    return response

# praiseObj 0代表问题点赞 1代表答案点赞
def praise_or_not(request):
    praiseObj = request.GET.get('praiseObj', None)
    status = request.GET.get('status', None)
    id = request.GET.get('id', None)

    # print(praiseObj,status,id)

    response = HttpResponse("0")
    if praiseObj and status and id:
        # 点赞动作
        if status == '0':
            try:
                if praiseObj == '0':
                    praisenum = Question.objects.get(id=id).praisenum
                    Question.objects.filter(id=id).update(
                        praisenum=praisenum + 1)

                elif praiseObj == '1':
                    praisenum = Answer.objects.get(id=id).praisenum
                    Answer.objects.filter(id=id).update(
                        praisenum=praisenum + 1)

                response = HttpResponse("1")
            except:
                response = HttpResponse("0")

        # 取消点赞动作
        else:
            try:

                if praiseObj == '0':
                    praisenum = Question.objects.get(id=id).praisenum
                    Question.objects.filter(id=id).update(
                        praisenum=praisenum-1)

                elif praiseObj == '1':
                    praisenum = Answer.objects.get(id=id).praisenum
                    Answer.objects.filter(id=id).update(praisenum=praisenum-1)
                response = HttpResponse("1")
            except:
                response = HttpResponse("0")

    return response


# 返回值含义:
# 0:请求参数为空 1:查询出错
# 'id', 'answer', 'answer_date', 'praisenum', 'replier_id', 'user.id_num', 'user.username', commentnum
# (0, u'对问题的评论'),
# (1, u'回复评论'),
@login_required()
def loadAnswer(request):
    qusid = request.GET.get('qusid', None)
    # print("qusid"+qusid)
    if qusid != None:
        try:
            # 获取系统推荐答案
            rec_aid = RecommendAns.objects.filter(qid=qusid).values_list('aid',flat=True)
            recommend = []
            for aid in rec_aid:
                ans = Answer.objects.filter(id=aid).values('id', 'answer', 'answer_date', 'praisenum', 'replier_id')[0]
                user = MyUser.objects.get(id=ans['replier_id'])
                ans['replier_id_num'] = ''
                ans['replier_name'] = '智能助教'
                recommend.append(ans)


            answer = Answer.objects.filter(question_id=qusid).values(
                'id', 'answer', 'answer_date', 'praisenum', 'replier_id')
            answer = list(answer)
            for ans in answer:
                user = MyUser.objects.get(id=ans['replier_id'])
                ans['replier_id_num'] = user.id_num
                ans['replier_name'] = user.username

            # 获取用户已经收藏的答案
            isCollect = Collection.objects.filter(
                owner=request.user, questionId=qusid)
            collectId = []
            if isCollect.exists():
                collectId = isCollect.values_list('ansId', flat=True)
                collectId = list(collectId)
            data = {'answer': answer, 'collectId': collectId,'recommend':recommend}
            return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")
        except Exception as e:
            print(str(e))
            return HttpResponse(1)
    else:
        return HttpResponse(0)

# 收藏和取消收藏
def collect_or_not(request):
    qid = request.GET.get('qid', None)
    aid = request.GET.get('aid', None)
    # status 0代表收藏  1代表取消收藏
    status = request.GET.get('status', None)
    print(qid, aid, status)
    if qid and aid and status:
        try:
            if status == "0":
                Collection.objects.create(
                    owner=request.user, questionId=qid, ansId=aid)
            else:
                Collection.objects.filter(
                    owner=request.user, questionId=qid, ansId=aid).delete()
            return HttpResponse("1")
        except:
            return HttpResponse("0")
    return HttpResponse("0")

# 异步加载问题数据
# 返回参数：字典{'id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum','description','username','answernum'}
def loadQuestion(request):
    qnum = request.COOKIES.get('qnum', 0)
    qnum = int(qnum)
    print('qnum:'+str(qnum))
    # print(qnum , qnum+LOAD_Q_NUM)
    question = Question.objects.order_by('-id').all().values('id', 'ques', 'update_date', 'tag',
                                    'asker_id', 'praisenum', 'description')[qnum:qnum+LOAD_Q_NUM]
    question = list(question)
    for q in (question):
        user = MyUser.objects.get(id=q['asker_id'])
        idnum = user.id_num
        if idnum:
            username = idnum + ' ' + user.username
        else:
            username = user.username
        answernum = Answer.objects.filter(question=q['id']).count()
        q['username'] = username
        q['answernum'] = answernum
    response = HttpResponse(json.dumps(
        question, cls=DateEncoder), content_type="application/json")
    response.set_cookie("qnum", qnum+LOAD_Q_NUM)
    return response


def getCollection(request):
    try:
        collects = request.user.my_collection.all().order_by('-id').values('questionId', 'ansId')
        # print(collects)
        collectList = []
        for c in collects:
            qus = Question.objects.get(id=c['questionId']).ques
            answer = Answer.objects.select_related(
                'replier').get(id=c['ansId'])

            c['qus'] = qus
            c['replier'] = answer.replier.username
            c['answer'] = answer.answer
            c['answer_date'] = answer.answer_date

            collectList.append(c)
        # print(collectList)
        return render(request, 'wenda/collection.html', {'collectList': collectList,'position':'collection'})
    except Exception as e:
        # print(str(e))
        return render(request,'wenda/error.html',{'errorMsg':"显示收藏出错"})
        # return HttpResponse("显示收藏出错")


# 我的提问
def myQuestion(request):
    try:
        MyUser = request.user
        quesList = MyUser.my_question.all().order_by(
            '-update_date').values('id', 'ques', 'update_date', 'praisenum')
        quesList = list(quesList)
        for q in quesList:
            ansNum = Answer.objects.filter(question_id=q['id']).count()
            q['ansNum'] = ansNum
        # print(quesList)
        return render(request, 'wenda/my_question.html', {'quesList': quesList,'position':'myask'})
    except Exception as e:
        # print(str(e))
        return render(request,'wenda/error.html',{'errorMsg':"访问我的问题出错！"})
        # return HttpResponse('访问我的问题出错！')


def qusDetail(request, qId):
    question = Question.objects.filter(id=qId).values(
        'id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum', 'description')
    if question.exists():
        question = list(question)
        for q in question:
            user = MyUser.objects.get(id=q['asker_id'])
            idnum = user.id_num
            if idnum:
                username = idnum + ' ' + user.username
            else:
                username = user.username
            answernum = Answer.objects.filter(question=q['id']).count()
            q['username'] = username
            q['answernum'] = answernum
            response = render(
                request, 'wenda/question_detail.html', {'question': question})
    else:
        response = render(request, 'wenda/question_detail.html',
                          {'question': None, 'getdetail': True})
    return response


# 获得一些答案数目小于3的问题
def load_want_answer(request):
    wnum = request.COOKIES.get('wnum',0)
    wnum = int(wnum)
    tobeAnswer = []
    itr = 0
    while len(tobeAnswer) < LOAD_Q_NUM and itr < 5:
        question = Question.objects.all().order_by('-id').values('id', 'ques', 'update_date', 'tag','asker_id', 'praisenum', 'description')[wnum:wnum+10]
        for q in question:
            user = MyUser.objects.get(id=q['asker_id'])
            answernum = Answer.objects.filter(question=q['id']).count()
            if answernum < 3:
                q['username'] = user.username
                q['answernum'] = answernum
                tobeAnswer.append(q)
        wnum += 10
        itr += 1
    tobeAnswer.sort(key=lambda q: q['answernum'])
    response = HttpResponse(json.dumps(tobeAnswer, cls=DateEncoder), content_type="application/json")
    response.set_cookie('wnum',wnum)
    return response



def want_answer(request):
    question = Question.objects.all().order_by('-id').values('id', 'ques', 'update_date', 'tag','asker_id', 'praisenum', 'description')[:20]
    tobeAnswer = []
    i = 0
    for q in question:
        i += 1
        user = MyUser.objects.get(id=q['asker_id'])
        answernum = Answer.objects.filter(question=q['id']).count()
        if answernum < 3:
            q['username'] = user.username
            q['answernum'] = answernum
            tobeAnswer.append(q)
        if len(tobeAnswer) > 5:
            break
    tobeAnswer.sort(key=lambda q: q['answernum'])
    response = render(request, 'wenda/want_answer.html',{'question': tobeAnswer,'position':'wantanswer'})
    response.set_cookie('wnum',i)
    return response

def invite(request):
    objId = request.GET.get('qid', None)
    rid = request.GET.get('uid', None)
    response = HttpResponse(0)
    if objId and rid:
        try:
            msg = Question.objects.get(id=objId).ques
            flag = createMsg(sid=request.user.id, rid=rid, message=msg, objId=objId, messagetype=1)
            if flag:
                response = HttpResponse(1)
        except:
            pass

    return response


# 搜索查询
def search(request):
	questionTail = request.GET.get('questionTail','')
	# questionClass = request.GET['questionClass']
	# return HttpResponse(questionTail + questionClass)
	if questionTail == '':
		response = HttpResponseRedirect("/wenda/")
	else:
		question = Question.objects.filter(ques__icontains=questionTail).values(
		    'id', 'ques', 'update_date', 'tag', 'asker_id', 'praisenum', 'description')
		if question.exists():
			question = list(question)
			for q in question:
			    user = MyUser.objects.get(id=q['asker_id'])
			    answernum = Answer.objects.filter(question=q['id']).count()
			    idnum = user.id_num
			    if idnum:
			        username = idnum + ' ' + user.username
			    else:
			        username = user.username
			q['username'] = username
			q['answernum'] = answernum
			response = render(request, 'wenda/search_result.html', {'question':question})
		else:
			response = render(request, 'wenda/search_result.html', {'question':None,'notfound':True})
	return response

question = Question.objects.all().order_by('-id').values('id', 'ques', 'update_date',
                                    'tag', 'asker_id', 'praisenum', 'description')[0:LOAD_Q_NUM]
def getInvitation(request):
    try:
        obj = Message.objects.filter(rid=request.user.id, messagetype=1).values_list('objId',flat=True)
        data = []
        for objId in obj:
            q = Question.objects.filter(id=objId).values('id', 'ques', 'update_date','tag', 'asker_id', 'praisenum', 'description')
            if q.exists():
                q = q[0]
                answernum = Answer.objects.filter(question=q['id']).count()
                user = MyUser.objects.get(id=q['asker_id'])
                q['answernum'] = answernum
                q['username'] = user.username
                data.append(q)
        # print(data)
        response = render(request,'wenda/invite_answer.html',{'question':data,'position':'myinvite'})
    except Exception as e:
        # print("error:"+str(e))
        response = render(request,'wenda/error.html',{'errorMsg':"跳转我的邀请页面出错，请稍后再试!"})
    return response

def toError(request):
    return render(request,'wenda/error.html',{'errorMsg':'测试页面'})

# 删除问题和对应的答案
def deleteQuestion(request):
    qid = request.GET.get('qid',None)
    response = HttpResponse(0)
    # 服务端判断用户是否试超级管理员
    # role=='a'表示时超级管理员
    role = getRole(request.user)
    if qid and role == 'a':
        try:
            q = Question.objects.get(id=qid)
            Answer.objects.filter(question=q).delete()
            RecommendAns.objects.filter(qid=q.id).delete()
            q.delete()
            response = HttpResponse(1)
        except Exception as e:
            pass
    return response

# 删除答案
def deleteAnswer(request):
    ansid = request.GET.get('ansid',None)
    response = HttpResponse(0)
    role = role = getRole(request.user)
    if ansid and role == 'a':
        try:
            Answer.objects.get(id=ansid).delete()
            response = HttpResponse(1)
        except:
            pass
    return response    

def compress(request):
    return render(request,'wenda/compress.html')

def loadAnswerForMessage(request):
    ansid = request.GET.get('ansid',None)
    response = HttpResponse("0")
    if ansid:
        try:
            answer = Answer.objects.filter(id=ansid).values('id', 'answer', 'answer_date', 'praisenum', 'replier_id')[0]
            user = MyUser.objects.get(id=answer['replier_id'])
            answer['replier_id_num'] = user.id_num
            answer['replier_name'] = user.username
            response = HttpResponse(json.dumps(answer, cls=DateEncoder), content_type="application/json")
        except Exception as e:
            # print(str(e))
            pass
    return response

import gensim
import jieba
import numpy as np
from scipy.linalg import norm
import math
import _thread

# 加载停止词
stopwords_set = set()
STOP_PATH = settings.USER_FILE_DIR + 'stopwords.txt'
stopwords = None
#stopwords = open(STOP_PATH,'r', encoding='utf-8')
# 加载训练好的词向量
model_file = settings.USER_FILE_DIR + 'train_150.bin'
model = None
#model = gensim.models.KeyedVectors.load_word2vec_format(model_file, binary=True)
# 将句子转换为向量
# s输入的句子 size词向量的维度
def sentence_vector(s,size):
    words = jieba.lcut(s,cut_all=False)
    v = np.zeros(size)
    for word in words:
        if word in model and word not in stopwords_set:
            v += model[word]
    return v

# 计算句子向量之间的相似度(余弦夹角)
def vector_similarity(v1,v2):
    m = norm(v1) * norm(v2)
    if m == 0:
        ans = 0.0
    else:
        ans = np.dot(v1,v2) / m
    return ans

# 获取推荐答案
def get_recommend_ans(qus,qid):
    # print("thread start with args:{0} {1}".format(qus,qid))
    try:
        v1 = sentence_vector(qus,150)
        # Question.objects.filter(id=qid).update(qVector=v1.tobytes())
        sim = 0
        ans = None
        for q in Question.objects.all().values('id','qVector'):
            if not q['qVector']:
                continue
            v2 = np.frombuffer(q['qVector'],dtype='float64')
            temp = vector_similarity(v1,v2)
            if temp > sim:
                sim = temp
                ans = q
        # print('ans:' + str(ans))
        Question.objects.filter(id=qid).update(qVector=v1.tobytes())
        # print("here is ok")
        if ans:
            # print('ans is find:'+str(ans['id']))
            recommend = Answer.objects.order_by('praisenum').filter(question_id=ans['id'])
            # print(recommend)
            if recommend.exists():
                # print('save ans')
                answer = recommend[0]
                RecommendAns.objects.create(qid=qid, aid=answer.id)
                # print("all is ok")
    except Exception as e:
        pass
        # print(str(e))
