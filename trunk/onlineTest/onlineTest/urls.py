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
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.static import serve
from auth_system.views import page_not_found, page_error, permission_denied
from mooc.views import get_Resource

urlpatterns = [
    url(r'^adm/', admin.site.urls, name='adminView'),
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    # url(r'^index/', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^accounts/', include('auth_system.urls')),
    url(r'^judge/', include('judge.urls')),
    url(r'^work/', include('work.urls')),
    url(r'^faq/', include('faq.urls')),
    url(r'^code_week/', include('code_week.urls')),
    # url(r'^weixin/', include('weixin.urls')),
    # url(r'^qqlogin/', include('qqlogin.urls')),
    url(r'^teetest/', include('teetest.urls')),
    url(r'^mooc/', include('mooc.urls')),
    url(r'get-Resource/', get_Resource,name='get_Resource'),
    url(r'^sign/', include('sign.urls')),
    url(r'^warning/', include('warning.urls')),
    url(r'^wenda/',include('wenda.urls')),
    url(r'^message/', include('message.urls')),
    # url(r'^media/(?P<path>.*)', serve, {'document_root':settings.MEDIA_ROOT}),
]

handler403 = permission_denied
#handler404 = page_not_found
#handler500 = page_error
