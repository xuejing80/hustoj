from django.conf.urls import url
from django.views.generic import TemplateView

from auth_system.views import UserControl, change_password, list_users, get_users, create_users, update_user, change_email
from . import views
urlpatterns = [
    url(r'^login/$', TemplateView.as_view(template_name="demo/login.html"), name='login'),
    url(r'^register/$', TemplateView.as_view(template_name="demo/register.html"), name='register'),
    #url(r'^changepassword/$', change_password, name='change_password'),
    url(r'^forgetpassword/$', TemplateView.as_view(template_name="demo/forgetpassword.html"), name='forget_password'),
    url(r'^resetpassword$', change_password, name='_resetpassword'),
    url(r'^resetpassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        TemplateView.as_view(template_name="demo/resetpassword.html")),
    url(r'^data/(?P<slug>\w+)$', UserControl.as_view(), name='data'),
    url(r'user-list$', list_users, name='user_list'),
    url(r'get-users$', get_users, name='get_users'),
    url(r'create-users$', TemplateView.as_view(template_name="add_users.html"), name='add_users'),
    url(r'update-user-$', update_user, name='_update_user'),
    url(r'update-user-(?P<pk>\d+)', update_user, name='update_user'),
    url(r'add-user$', create_users, name='create_users'),
    url(r'^change_email/$', change_email, name='change_email'),
    url(r'^resetpassword_mail$', change_email, name='_resetpassword_mail'),
    url(r'^resetpassword_mail/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<umailb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        TemplateView.as_view(template_name="demo/resetpassword_mail.html")),
    url(r'^dashboard$', views.dash_board, name='dashboard'),
]
