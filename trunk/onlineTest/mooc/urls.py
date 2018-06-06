from django.conf.urls import url
from mooc.views import get_courser_name,type_resource,add_type,add_resource,list_course,list_resource,resource_show,update_resource,del_resource,ResourceDetailView,uploud_file

urlpatterns = [
    url(r'^get-courser-name',get_courser_name, name='get_courser_name'),
    url(r'^resource-type', type_resource, name='type_resource'),
    url(r'^add_type', add_type, name='add_type'),
    url(r'^course-list-$', list_course, name='_list_course'),
    url(r'^course-list-(?P<id>\d+)/$', list_course, name='list_course'),
    url(r'^show-resource-(?P<id>\d*)/$', resource_show, name='resource_show'),
    url(r'^resource-list', list_resource, name='list_resource'),
    url(r'resource-add', add_resource, name='add_resource'),
    url(r'^del-resource',del_resource,name='del_resource'),
    url(r'update-resource-$',update_resource,name='_update_resource'),
    url(r'update-resource-(?P<id>\d+)/$',update_resource,name='update_resource'),
    url(r'^resource-detail-$',ResourceDetailView.as_view(),name='_resource_detail'),
    url(r'^resource-detail-(?P<pk>\d+)/$',ResourceDetailView.as_view(),name='resource_detail'),

    url(r'upload-file',uploud_file,name='uploud_file'),
]