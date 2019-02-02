
from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'auth',auth_view),
    url(r'addstudent',addstudent),
    url(r'addfaculty',addfaculty),
    url(r'add_faculty',add_faculty),
    url(r'add_student',add_student),
    url(r'addtopastfaculty',addtopastfaculty),
    url(r'addtoactivefaculty',addtoactivefaculty),
    url(r'addtopaststudent',addtopaststudent),
    url(r'addtoactivestudent',addtoactivestudent),
    url(r'removefaculty',removefaculty),
    url(r'removestudent',removestudent),
    url(r'login',login),
    url(r'logout',logout),
    url(r'',login)
]
