from django.conf.urls import url
from django.views.generic import TemplateView
from auth_system.views import UserControl
from . import views

urlpatterns = [
    url(r'^login/$', TemplateView.as_view(template_name="demo/login.html"), name='login'),
    url(r'^register/$', TemplateView.as_view(template_name="demo/register.html"), name='register'),
    # 此处为了兼容学生初始邮箱无效的情况，重新设计了修改密码的模块，替换了系统原来的change_password
    # url(r'^changepassword/$', views.change_password, name='change_password'),
    url(r'^change_email/$', views.change_email, name='change_email'),
    url(r'^resetpassword_mail/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<umailb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        TemplateView.as_view(template_name="demo/resetpassword_mail.html"), name='resetpassword_mail'),
    # 接下来的两个url用于忘记密码的情况
    url(r'^forgetpassword/$', TemplateView.as_view(template_name="demo/forgetpassword.html"), name='forget_password'),
    url(r'^resetpassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        TemplateView.as_view(template_name="demo/resetpassword.html"), name='resetpassword'),
    # 接下来的两个url用于显示用户列表和获取用户列表数据
    url(r'^user-list/$', views.list_users, name='user_list'),
    url(r'^get-users/$', views.get_users, name='get_users'),
    # 为了确保系统的安全性，禁用了批量增加用户的功能
    # url(r'^create-users$', views.create_users, name='create_users'),
    url(r'^update-user/$', views.update_user, name='update_user'),
    # 接下来的这个url用来处理页面发送的各种动作请求
    url(r'^data/(?P<slug>\w+)$', UserControl.as_view(), name='data'),
    url(r'^dashboard/$', views.dash_board, name='dashboard'),
    url(r'^monitor/$', views.monitor, name='monitor'),
]
