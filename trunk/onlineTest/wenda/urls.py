#-*- conding:utf-8 -*-

from wenda.views import *
from django.conf.urls import url
from wenda.upload import imageUpload

urlpatterns = [
    # 问答首页
	url(r'^$',index,name='wenda_index'),
    # 上传图片
	url(r'upload/media/(?P<dirName>[^/]+)', imageUpload),
    # 跳转提问页面
	url(r'ask/$',ask,name='to_ask_question'),
    # 上传提问的问题
	url(r'submitqus/$', submitqus, name='submitqus'),
	# 点击一个问题的链接跳转到回答页面
	url(r'question/answer/(?P<qId>\d+)/$', question_answer, name='question_answer'), 
	# 回答问提交
 	url(r'submit_answer/$', submitAnswer, name='submitAnswer'),
	# 点赞和取消点赞
	url(r'praise_or_not/$', praise_or_not,name='praise_or_not'),
    # 异步加载答案
	url(r'load_answer/$', loadAnswer, name='loadAnswer'),
    # 收藏或取消收藏
	url(r'collect_or_not/$', collect_or_not, name='collect_or_not'),
    # 异步加载更多问题
	url(r'load_question/$', loadQuestion, name='load_question'),
	# 跳转我的收藏页面
	url(r'get_collection/$',getCollection,name='to_my_collection'),
	# 跳转我的提问页面
	url(r'get_my_question/$',myQuestion,name='to_my_question'),
	# 获取问题详细信息
	url(r'qusdetail/(?P<qId>\d+)$', qusDetail, name='qusdetail'),
	# 想要回答的跳转页面
	url(r'want_answer/$', want_answer, name='want_answer'),
	# 邀请其他人回答
	url(r'invite/$',invite, name='invite'),
    # 搜索问题
    url(r'search/$',search, name='search'),
    # 获取被邀请回答的问题
    url(r'get_invitation/$',getInvitation, name='get_invitation'),
    # 出错显示页面
    url(r'error/$',toError, name='toError'),
    # 删除问题（同时会删除问题对应的答案）
    url(r'delete_question/$',deleteQuestion, name='delete_question'),
    # 删除答案
    url(r'detele_answer/$',deleteAnswer, name='delete_answer'),
    # 加载图片
    url(r'^get_img/(?P<path>.+)',getImg, name='get_img'),
    # 消息页面异步加载答案
    url(r'load_answer_message/',loadAnswerForMessage, name='load_answer_message'),
]
