from django.conf.urls import  url

urlpatterns = [
    url(r'^pc-geetest/register', 'teetest.views.pcgetcaptcha', name='pcgetcaptcha'),
    url(r'^mobile-geetest/register', 'teetest.views.mobilegetcaptcha', name='mobilegetcaptcha'),
    url(r'^pc-geetest/validate$', 'teetest.views.pcvalidate', name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate','teetest.views.pcajax_validate', name='pcajax_validate'),
    url(r'^mobile-geetest/ajax_validate','teetest.views.mobileajax_validate', name='mobileajax_validate'),
    #url(r'/*', 'teetest.views.home', name='home'),
]
