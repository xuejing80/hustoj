"""onlineTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from judge.views import get_json

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='adminView'),
    url(r'^index/', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^accounts/', include('auth_system.urls')),
    url(r'^judge/', include('judge.urls')),
    url(r'^work/', include('work.urls')),
    url(r'get-json-(?P<model_name>\w+)/$', get_json,name='get_json'),
    url(r'^$', TemplateView.as_view(template_name="index.html")),
    
]
