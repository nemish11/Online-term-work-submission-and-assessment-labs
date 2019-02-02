from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'new_assignment',new_assignment),
    url(r'newassignment',newassignment),
    url(r'showAssignment',showAssignment),
    url(r'submitcode',submitcode),
    #url(r'uploadfiles',uploadfiles),
    url(r'addweek',addweek),
    url(r'previous_submissions',previous_submissions),
    #url(r'addinputfiles',addinputfiles),
    url(r'submission_files',submission_files),
    url(r'selectedsubmission',selectedsubmission),
    url(r'deleteAssignment',deleteAssignment),
    url(r'runcode',runcode),
    url(r'selectedAssignment',selectedAssignment),
    url(r'showWeek',showWeek),
    url(r'deleteweek',deleteweek),
    url(r'',showWeek),
]
