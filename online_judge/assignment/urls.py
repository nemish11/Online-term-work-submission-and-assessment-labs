from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'new_assignment',new_assignment),
    url(r'newassignment',newassignment),
    url(r'showAssignment',showAssignment),
    url(r'submitcode',submitcode),
    url(r'uploadfiles',uploadfiles),
    url(r'addweek',addweek),
    url(r'showWeek',showWeek),
    url(r'',showWeek),
]
