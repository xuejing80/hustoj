from django.conf.urls import url, include
from .views import  select_point, delete_problem, add_problem, ProblemDetailView, update_problem, \
    add_choice, list_problems,list_choices,del_choice_problem,ChoiceProblemDetailView,update_choice_problem, verify_file

urlpatterns = [
    url(r'problem_list/$', list_problems, name='problemlist'),
    url(r'choice_problem_list',list_choices,name='choice_problem_list'),
    url(r'^del-problem/$', delete_problem, name='del_problem'),
    url(r'^del-choice-problem',del_choice_problem,name='del_choice_problem'),
    url(r'add-problem', add_problem, name='add_problem'),
    url(r'pointslect', select_point, name='select_point'),
    url(r'^problem-detail-$', ProblemDetailView.as_view(), name='_problem_detail'),
    url(r'^choice-detail-$',ChoiceProblemDetailView.as_view(),name='_choice_problem_detail'),
    url(r'^update-biancheng-$', update_problem, name='_update_problem'),
    url(r'update-choice-$',update_choice_problem,name='_update_choice_problem'),
    url(r'^problem-detail-(?P<pk>\d+)/$', ProblemDetailView.as_view(), name='problem_detail'),
    url(r'^choice-detail-(?P<pk>\d+)/$',ChoiceProblemDetailView.as_view(),name='choice_problem_detail'),
    url(r'^update-biancheng-(?P<id>\d*)/$', update_problem, name='update_problem'),
    url(r'update-choice-(?P<id>\d+)/$',update_choice_problem,name='update_choice_problem'),
    url(r'add-choice', add_choice, name='add_choice_problem'),
    url(r'verify-file',verify_file,name='verify_file'),
]
