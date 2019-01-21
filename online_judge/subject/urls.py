from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [

    url(r'all_subject', all_subject),
    url(r'add_subject', add_subject),
    url(r'remove_subject', remove_subject),
    url(r'request_subject', request_subject),
    url(r'request_list', request_list),
    url(r'', all_subject),

]