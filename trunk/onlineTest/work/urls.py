from django.conf.urls import url, include

from work.views import add_homework, get_json_work, list_homework, del_homework, show_homework, \
    ajax_for_homework_info, do_homework, add_banji, add_courser, get_banji_list, list_banji, del_banji, update_banji, \
    copy_to_my_homework, list_my_homework, update_public_homework, update_my_homework, show_my_homework, show_banji, \
    add_students, ajax_add_students, assign_homework, list_do_homework, get_my_homework_todo, show_homework_result, \
    list_finished_homework, get_finished_homework, get_finished_students, list_coursers, list_kp1s, list_kp2s, \
    delete_courser, add_kp1, add_kp2, delete_kp1, delete_kp2, add_myhomework, test_run, delete_homeworkanswer, \
    rejudge_homework, save_homework_temp, init_homework_data, file_download

urlpatterns = [
    url(r'del-homeworkanswer-(?P<id>\d+)', delete_homeworkanswer, name='delete_homeworkanswer'),
    url(r'del-homeworkanswer-', delete_homeworkanswer, name='_delete_homeworkanswer'),
    url(r'add-homework$', add_homework, name='add_homework'),
    url(r'get-json-work', get_json_work, name='get_json_data'),
    url(r'^homework-list', list_homework, name='homework_list'),
    url(r'del-homework', del_homework, name='del_homework'),
    url(r'^homework-detail-$', show_homework, name='_homework_detail'),
    url(r'update-public-homework-$', update_public_homework, name='_update_public_homework'),
    url(r'update-my-homework-$', update_my_homework, name='_update_my_homework'),
    url(r'do_homework$', do_homework, name='_do_homework'),
    url(r'update-banji-$', update_banji, name='_update_banji'),
    url(r'my-homework-detail-$', show_my_homework, name='_my_homework_detail'),
    url(r'banji-detail-$', show_banji, name='_banji_detail'),
    url(r'add-students-to-mybanji-$', add_students, name='_add_students'),
    url(r'homework-result-$', show_homework_result, name='_show_homework_result'),
    url(r'^homework-detail-(?P<pk>\d+)/$', show_homework, name='homework_detail'),
    url(r'update-public-homework-(?P<pk>\d+)', update_public_homework, name='update_public_homework'),
    url(r'update-my-homework-(?P<pk>\d+)', update_my_homework, name='update_my_homework'),
    url(r'get_homework_info', ajax_for_homework_info, name='get_homework_info'),
    url(r'do_homework(?P<homework_id>\d+)', do_homework, name='do_homework'),
    url(r'add_banji', add_banji, name='add_banji'),
    url(r'add_courser', add_courser, name='add_courser'),
    url(r'get_banji_list', get_banji_list, name='get_banji_list'),
    url(r'banji-list', list_banji, name='banji_list'),
    url(r'del-banji', del_banji, name='del_banji'),
    url(r'update-banji-(?P<id>\d+)', update_banji, name='update_banji'),
    url(r'copy-to-myhomework', copy_to_my_homework, name='copy_to_my_homework'),
    url(r'my_homework_list', list_my_homework, name='my_homework_list'),
    url(r'my-homework-detail-(?P<pk>\d+)', show_my_homework, name='my_homework_detail'),
    url(r'banji-detail-(?P<pk>\d+)', show_banji, name='banji_detail'),
    url(r'add-students-to-mybanji-(?P<pk>\d+)', add_students, name='add_students'),
    url(r'add-students', ajax_add_students, name='ajax_add_students'),
    url(r'assign-homework', assign_homework, name='assign_homework'),
    url(r'do-homework-list', list_do_homework, name='list_do_homework'),
    url(r'get-do-homework-data', get_my_homework_todo, name='get_my_homework_todo'),
    url(r'homework-result-(?P<id>\d+)', show_homework_result, name='show_homework_result'),
    url(r'list-finished-homework', list_finished_homework, name='list_finished_homework'),
    url(r'get-finished-homework-list', get_finished_homework, name='get_finished_homework'),
    url(r'get-finished-student', get_finished_students, name="get_finished_students"),
    url(r'courser-list', list_coursers, name='list_coursers'),
    url(r'kp1-list-(?P<id>\d+)', list_kp1s, name='list_kp1s'),
    url(r'kp2-list-(?P<id>\d+)', list_kp2s, name='list_kp2s'),
    url(r'delete-courser', delete_courser, name='delete_courser'),
    url(r'add-kp1', add_kp1, name='add_kp1'),
    url(r'add-kp2', add_kp2, name='add_kp2'),
    url(r'delete-kp1', delete_kp1, name='delete_kp1'),
    url(r'delete-kp2', delete_kp2, name='delete_kp2'),
    url(r'add-myhomework', add_myhomework, name='add_myhomework'),
    url(r'test_run', test_run, name='test_run'),
    url(r'rejudge-homework-$', rejudge_homework, name='_rejudge_homework'),
    url(r'rejudge-homework-(?P<id>\d+)', rejudge_homework, name='rejudge_homework'),
    url(r'save-homework',save_homework_temp,name='save_homework'),
    url(r'get-init-homework-data',init_homework_data,name='get_init_homework_data'),
    url(r'download',file_download,name='download')
]
