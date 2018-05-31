from django.conf.urls import url
from warning.views import warning

urlpatterns = [
    url(r'^$', warning),
]
