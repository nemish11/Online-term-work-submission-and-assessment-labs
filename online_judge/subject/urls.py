
from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [

    url(r'all_subject', all_subject),
    url(r'addsubject',addsubject),
    url(r'add_subject', add_subject),
    url(r'removesubject', removesubject),
    url(r'remove_subject', remove_subject),
    url(r'request_subject', request_subject),
    url(r'pending_request', pending_request),
    url(r'request_list', request_list),
    url(r'approved_request', approved_request),
    url(r'go_next', go_next),
    url(r'go_next/$', go_next, name="go-next"),
    url(r'', all_subject),

]
