from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^oauth/qq/login/$', qq_login, name='qq_login'),
    url(r'^oauth/qq/check/$', qq_check, name='qq_check'),
    url(r'^oauth/bind/account/$', qq_login, name='bind_account'),
]

