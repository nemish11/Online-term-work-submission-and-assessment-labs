from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    url(r'studentlist_for_assignment',studentlist_for_assignment),
    url(r'new_assignment1',new_assignment1),
    url(r'import_assignment1',import_assignment1),
    url(r'new_assignment',new_assignment),
    url(r'import_assignment',import_assignment),
    url(r'importassignment',importassignment),
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
    url(r'savecomment',savecomment),
    url(r'markcomment',markcomment),
    url(r'',showWeek),
]
