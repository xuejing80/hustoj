from channels import route
from .consumers import *

# channel_routing = {
#     # This makes Django serve static files from settings.STATIC_URL, similar
#     # to django.views.static.serve. This isn't ideal (not exactly production
#     # quality) but it works for a minimal example.
#
#     # Wire up websocket channels to our consumers:
#     'websocket.connect': consumers.ws_connect,
#    # 'websocket.receive': consumers.ws_receive,
#     'websocket.disconnect': consumers.ws_disconnect,
# }

code_week_routing = [
    route("websocket.connect", ws_connect_teacher_detail, path=r'^/code_week/course-(?P<courseId>\d+)/$'),
    route("websocket.disconnect", ws_disconnect_teacher_detail, path=r'^/code_week/course-(?P<courseId>\d+)/$'),
    route("websocket.connect", ws_connect_student_detail, path=r'^/code_week/course_(?P<courseId>\d+)/$'),
    route("websocket.receive", ws_receive_student_detail, path=r'^/code_week/course_(?P<courseId>\d+)/$'),
    route("websocket.disconnect", ws_disconnect_student_detail, path=r'^/code_week/course_(?P<courseId>\d+)/$'),
    route("websocket.connect", ws_connect_teacher_latest_info, path=r'^/code_week/course-latest-info-(?P<courseId>\d+)/$'),
    route("websocket.disconnect", ws_disconnect_teacher_latest_info, path=r'^/code_week/course-latest-info-(?P<courseId>\d+)/$'),
]