from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views

urlpatterns = [
    url(r'change_passwordbyfaculty',change_passwordbyfaculty),
    url(r'change_password_by_faculty',change_password_by_faculty),
    url(r'change_password_done', change_password_done),
    url(r'change_password',change_password),
    url(r'updateStudent',updateStudent),
    url(r'update_student', update_student),
    url(r'allsubmissions',allsubmissions),
    url(r'updateFaculty',updateFaculty),
    url(r'updateAdmin',updateAdmin),
    url(r'update_faculty',update_faculty),
    url(r'update_admin',update_admin),
    url(r'shownotifications',shownotifications),
    url(r'profile',profile),
    url(r'',profile)
]
