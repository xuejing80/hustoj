from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^course_list/$', course_list_for_student, name='course_list_for_student'),
    url(r'^courses/$', course_list_for_teacher, name='course_list_for_teacher'),
    url(r'^add_course/$', add_course, name='add_codeweek_course'),
    url(r'^course-(?P<courseId>\d+)/$', view_course, name='view_course_for_teacher'),
    url(r'^course_(?P<courseId>\d+)/$', student_view_course, name='view_course_for_student'),
    url(r'^sheji_problem_list/', list_sheji, name='sheji_problem_list'),
    url(r'^del-sheji/$', delete_sheji, name='del_sheji'),
    url(r'^sheji-detail-$',ShejiProblemDetailView.as_view(),name='_sheji_problem_detail'),
    url(r'^update-sheji-$', update_sheji, name='_update_sheji'),
    url(r'^sheji-detail-(?P<pk>\d+)/$',ShejiProblemDetailView.as_view(),name='sheji_detail'),
    url(r'^update-sheji-(?P<id>\d*)/$', update_sheji, name='update_sheji'),
    url(r'add-sheji', add_sheji, name='add_sheji'),
    url(r'get-sheji/$', get_json_sheji, name='get_json_sheji'),
    url(r'get-problem-student-(?P<id>\d+)/$', get_problem_student, name='get_problem_student'),
    url(r'download-(?P<fileId>\d+)/$', download, name='download_file'),
    url(r'student-info-(?P<courseId>\d+)/$', student_info, name='student_info'),
    url(r'^teacher_update/$', teacher_update_info, name='teacher_update_course'),
    url(r'teacher-info-(?P<courseId>\d+)/$', teacher_course_info, name='teacher_course_info'),
]