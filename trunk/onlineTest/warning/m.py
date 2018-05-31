# -*- coding:utf-8 -*-
from auth_system.models import MyUser
from work.models import BanJi,MyHomework,HomeworkAnswer
from judge.models import ChoiceProblem
from warning.models import WarningData
import re
import datetime
import os
import json
from django.conf import settings
from warning import gcp

now = datetime.datetime.now()
homeworkstarttime= now - datetime.timedelta(days=30)
homeworkendtime=now + datetime.timedelta(days=7)
domain = settings.SITE_DOMAIN

def getAllTeachers():	
	return MyUser.objects.filter(groups__pk='1')

def getBanjiofTeacher(id):
	return BanJi.objects.filter(teacher_id=id).filter(end_time__gte = now)

def getMyHomeworkList(id):
	return MyHomework.objects.filter(start_time__gte = homeworkstarttime).filter(end_time__lte = homeworkendtime).filter(banji__id=id)

def getStudentsList(banjiid,teacherid):
	return BanJi.objects.filter(id=banjiid).first().students.all().exclude(id_num=teacherid)

def getChoiceInfoListByIds(ids):
	return ChoiceProblem.objects.in_bulk(ids)

def getGoodAndBadStu(stuids,homeworkid):
	goodstu = ''
	badstu = ''
	sql = "creator_id in ("
	for id in stuids:
		sql = sql + str(id) + ','
	sql = sql[:-1] + ')'
	res = HomeworkAnswer.objects.extra(where=[sql]).filter(homework_id=homeworkid).order_by('-score','create_time')
	if len(res) > 5:
		for i in res[:5]:
			goodstu = goodstu + i.creator.username + "(" + i.creator.id_num + ":" + str(i.score) + "分); "
		for i in res.reverse()[:5]:
			if i.score < i.homework.total_score:
				badstu = badstu + i.creator.username + "(" + i.creator.id_num + ":" + str(i.score) + "分);"
	return goodstu,badstu


def getDict():
	path = '/home/judge/log/'
	files = os.listdir(path)
	resultdict={}
	for file in files:
		if file.find("detail")!=0:
			continue
		#print(file)
		f = open(path+file,'r',encoding="UTF-8")		
		for line in f:
			if line[:2] == ">>":
				logtime = datetime.datetime.strptime(line[3:22],"%Y-%m-%d %H:%M:%S")
				if logtime >= homeworkstarttime:
					if(re.search('提交',line)):
						s=re.findall(r"selection-\d+': '[a-d]",line)
						d = {}
						if s:
							for one in s:
								d[re.search(r'\d+',one).group()] =  one[-1]									
						a=re.split(":|\：|\(|\)|\，",line)
						key = a[8]+a[11]
						item=[]
						if key in resultdict:
							item = resultdict[key]
						item.append(d)
						resultdict[key]=item
	return resultdict



def warning():
	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"begin...")
	mydict = getDict()
	teacherList = getAllTeachers()
	for teacher in teacherList:
		# if teacher.username != '薛景老师':
		# 	continue
		msgteacher = "%s 老师您好:\n"%teacher.username
		banjiList = getBanjiofTeacher(teacher.id)
		msgbanji = ''
		for banji in banjiList:
			homeworkList = getMyHomeworkList(banji.id)
			studentList = getStudentsList(banji.id,teacher.id)
			msghomework = ''
			for homework in homeworkList:
				choiceListStr = homework.choice_problem_ids
				choiceidList = []
				choiceinfoList = []
				if choiceListStr != '':
					choiceidList = re.split(',',choiceListStr)
					if choiceidList[-1] == '':
						choiceidList = choiceidList[:-1]
					choiceinfoList = getChoiceInfoListByIds(choiceidList)
				total = 0
				stuids = []
				goodstu = ""
				badstu = ""
				chwresult = {}
				finishstudentlist = homework.finished_students.all()
				for student in studentList:
					stuids.append(student.id)
					if student in finishstudentlist:
						total = total + 1
					keyd = str(student.id_num) + str(homework.id)
					if keyd in mydict:						
						item = mydict[keyd]
						if choiceidList:
							for answerdict in item:
								for key,value in choiceinfoList.items():
									if str(key) in answerdict.keys():
										if key in chwresult:
											tempdict = chwresult[key]
											tempdict[answerdict.get(str(key))] = tempdict[answerdict.get(str(key))] + 1
											tempdict['t'] = tempdict.get('t') + 1
											if value.right_answer != answerdict.get(str(key)):
												tempdict['w'] = tempdict['w'] + 1
										else:
									 		tempdict = {'a':0,'b':0,'c':0,'d':0,'w':0,'t':1}
									 		tempdict[answerdict.get(str(key))] = 1
									 		if value.right_answer != answerdict.get(str(key)):
									 			tempdict['w'] = tempdict['w'] + 1
									 		chwresult[key] = tempdict
						del mydict[keyd]

				copydict = {}
				if stuids:
					goodstu,badstu = getGoodAndBadStu(stuids,homework.id)
					copydict = gcp.getCopyGroups(homework.id,stuids)
				
				msghomework = "\n  %s 班级的作业《%s》(起止时间：%s--%s) 完成情况如下：\n      全班共有%d人，已交作业%d份。"%(banji.name,homework.name,homework.start_time.strftime("%Y-%m-%d"),homework.end_time.strftime("%Y-%m-%d"),len(studentList),total)
				msghomework = msghomework + " 详情请点击链接查看： http://"+ domain + "/work/my-homework-detail-" + str(homework.id) + "\n"
				if goodstu:
					msghomework = msghomework + "      成绩较好的同学有:" + goodstu + "\n"
				if badstu:
					msghomework = msghomework + "      成绩较差的同学有:" + badstu + "\n"
				if chwresult:
					jsdata = json.dumps(chwresult)
					w = WarningData(data = jsdata,tid = teacher.id)
					w.save()					
					msghomework = msghomework + "      错误的选择题请点击链接查看（按错误率排序）： http://" + domain + "/warning?id="+ str(w.id) +"\n"
				
				if copydict:
					msghomework = msghomework + '      依据程序相似度匹配算法，我们发现以下同学的作业相似度较高，请您及时关注是否存在作业抄袭现象：\n'
					for key in copydict:
						msghomework = msghomework + '        (' + key + ' ' + copydict[key] + ')\n'

			if msghomework:
				msgbanji = msgbanji + msghomework
		if msgbanji:
			msgteacher = msgteacher + msgbanji
			sendMailToTeacher(msgteacher,teacher.email)
			#print(msgteacher)
	print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"end")
			

def sendMailToTeacher(msg,emailaddress):
	title = "作业完成情况反馈"
	from_email = settings.EMAIL_HOST_USER

	os.system("echo '%s' | mail -s %s %s -aFrom:%s\<%s\>" % (msg,title,emailaddress,settings.ADMINS[0][0],settings.ADMINS[0][1]))

