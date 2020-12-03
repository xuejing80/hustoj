from django.conf.urls import url, include

from work.views import *

urlpatterns = [
    url(r'^courser-list/$', list_coursers, name='list_coursers'),
    url(r'^add_courser/$', add_courser, name='add_courser'),
    url(r'^delete-courser/$', delete_courser, name='delete_courser'),
    url(r'^kp1-list/(?P<id>\d+)/$', list_kp1s, name='list_kp1s'),
    url(r'^kp2-list/(?P<id>\d+)/$', list_kp2s, name='list_kp2s'),
    url(r'^add-kp1/$', add_kp1, name='add_kp1'),
    url(r'^add-kp2/$', add_kp2, name='add_kp2'),
    url(r'^delete-kp1/$', delete_kp1, name='delete_kp1'),
    url(r'^delete-kp2/$', delete_kp2, name='delete_kp2'),

    url(r'^banji-list/$', list_banji, name='banji_list'),
    url(r'^get_banji_list/$', get_banji_list, name='get_banji_list'),
    url(r'^add_banji/$', add_banji, name='add_banji'),
    url(r'^del-banji/$', del_banji, name='del_banji'),
    url(r'^update-banji/$', emptyView, name='_update_banji'),
    url(r'^update-banji/(?P<id>\d+)/$', update_banji, name='update_banji'),
    url(r'^banji-detail/$', emptyView, name='_banji_detail'),
    url(r'^banji-detail/(?P<pk>\d+)/$', show_banji, name='banji_detail'),
    url(r'^get-students/(?P<banji>\d+)/$', get_students, name='get_students'),
    url(r'^reset-stupassword/$', reset_stupassword,name='reset_stupassword'),
    url(r'^del-students/$', del_students,name='del_students'),
    url(r'^add-students-to-mybanji/$', emptyView, name='_add_students'),
    url(r'^add-students-to-mybanji/(?P<pk>\d+)/$', add_students, name='add_students'),
    url(r'^add-students/$', ajax_add_students, name='ajax_add_students'),

    url(r'^homework-list/$', list_homework, name='homework_list'),
    url(r'^get-worklist/$', get_json_work, name='get_json_work'),
    url(r'^add-homework/$', add_homework, name='add_homework'),
    url(r'^update-public-homework/$', emptyView, name='_update_public_homework'),
    url(r'^update-public-homework/(?P<pk>\d+)/$', update_public_homework, name='update_public_homework'),
    url(r'^del-homework/$', del_homework, name='del_homework'),
    url(r'^homework-detail/$', emptyView, name='_homework_detail'),
    url(r'^homework-detail/(?P<pk>\d+)/$', show_homework, name='homework_detail'),

    url(r'^my_homework_list/$', list_my_homework, name='my_homework_list'),
    url(r'^add-myhomework/$', add_myhomework, name='add_myhomework'),
    url(r'^update-my-homework/$', emptyView, name='_update_my_homework'),
    url(r'^update-my-homework/(?P<pk>\d+)/$', update_my_homework, name='update_my_homework'),
    url(r'^my-homework-detail/$', emptyView, name='_my_homework_detail'),
    url(r'^my-homework-detail/(?P<pk>\d+)/$', show_my_homework, name='my_homework_detail'),
    url(r'^get_homework_info/$', ajax_for_homework_info, name='get_homework_info'),
    url(r'^get-finished-student/$', get_finished_students, name="get_finished_students"),
 
    url(r'^copy-to-myhomework/$', copy_to_my_homework, name='copy_to_my_homework'),
    url(r'^get_assign_status/$', get_assign_status, name='get_assign_status'),
    url(r'^assign-homework/$', assign_homework, name='assign_homework'),
    url(r'^unassign-homework/$', unassign_homework, name='unassign_homework'),

    url(r'^do-homework-list/$', list_do_homework, name='list_do_homework'),
    url(r'^get-do-homework-data/$', get_my_homework_todo, name='get_my_homework_todo'),
    url(r'^homework-result/$', emptyView, name='_show_homework_result'),
    url(r'^homework-result/(?P<id>\d+)/$', show_homework_result, name='show_homework_result'),
    url(r'^do_homework/$', emptyView, name='_do_homework'),
    url(r'^do_homework/(?P<homework_id>\d+)/$', do_homework, name='do_homework'),
    url(r'^get-init-homework-data/$', init_homework_data, name='get_init_homework_data'),
    url(r'^test_run/$', test_run, name='test_run'),
    url(r'^save-homework/$', save_homework_temp, name='save_homework'),
    url(r'^rejudge-homework/$', emptyView, name='_rejudge_homework'),
    url(r'^rejudge-homework/(?P<id>\d+)/$', rejudge_homework, name='rejudge_homework'),
    url(r'^homework-result-comment_change/$', comment_change, name='comment_change'),
    url(r'^del-homeworkanswer/$', emptyView, name='_delete_homeworkanswer'),
    url(r'^del-homeworkanswer/(?P<id>\d+)/$', delete_homeworkanswer, name='delete_homeworkanswer'),

    url(r'^list-finished-homework/$', list_finished_homework, name='list_finished_homework'),
    url(r'^get-finished-homework-list/$', get_finished_homework, name='get_finished_homework'),
    url(r'^get-finished-homework-workInformation/$', get_finished_homework_workInformation, name='get_finished_homework_workInformation'),

    # 下载模块是静态页面，内容不更新，干脆禁用了
    # url(r'^download/$', file_download, name='download'),
    url(r'^send_zipfile/$', emptyView, name='_send_zipfile'),
    url(r'^send_zipfile/(\d+)/$', send_zipfile, name='send_zipfile'),

    # 2020年11月增加了关于MOOC成绩统计的功能
    url(r'^mooc-once-analyse-', once, name='once'),
    url(r'^get_score_list', get_score_list, name='get_score_list'),
]
