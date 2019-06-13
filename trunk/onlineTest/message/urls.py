from wenda.views import *
from django.conf.urls import url
from django.contrib import admin
from message.views import *
urlpatterns = [
    # 跳转我的消息页面
    url(r'to_message/', toMessage, name='to_message'),
    # 设置消息已读
    url(r'read_message',readMessage, name='read_message'),
    # 加载已读历史消息
    url(r'load_message',loadMessage, name='load_message'),
]
