from django.conf.urls import url, include
from faq.views import index, send

urlpatterns = [
    url(r'send/$', send, name='send'),
    url(r'^$', 'faq.views.index'),
]
