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
from django.views.generic.base import RedirectView
from auth_system.views import page_not_found, page_error, permission_denied

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    url(r'^adm/', admin.site.urls, name='adminView'),
    url(r'^index/', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^accounts/', include('auth_system.urls')),
    url(r'^judge/', include('judge.urls')),
    url(r'^work/', include('work.urls')),
    url(r'^faq/', include('faq.urls')),
    url(r'^weixin/', include('weixin.urls')),
    url(r'get-json-(?P<model_name>\w+)/$', get_json,name='get_json'),
    url(r'^favicon\.ico$',favicon_view),
    url(r'^$', TemplateView.as_view(template_name="index.html")),
]

handler403 = permission_denied
handler404 = page_not_found
handler500 = page_error
