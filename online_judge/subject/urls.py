from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'set_subject_for_studentlist',set_subject_for_studentlist),
    url(r'student_list',student_list),
    url(r'readd_subject', readd_subject),
    url(r'all_subject', all_subject),
    url(r'addsubject',addsubject),
    url(r'add_subject', add_subject),
    url(r'removesubject', removesubject),
    url(r'request_subject', request_subject),
    url(r'pending_request', pending_request),
    url(r'request_list', request_list),
    url(r'approved_request', approved_request),
    url(r'removerequest',removerequest),
    url(r'remove_student', remove_student),
    url(r'', all_subject),

]
