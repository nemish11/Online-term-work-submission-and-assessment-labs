
from django.conf.urls import url
from django.urls import path
from .views import auth_view,login,logout,add_faculty,add_student,addfaculty,addstudent
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'auth',auth_view),
    url(r'addstudent',addstudent),
    url(r'addfaculty',addfaculty),
    url(r'add_faculty',add_faculty),
    url(r'add_student',add_student),
    url(r'login',login),
    url(r'logout',logout),
    url(r'',login)
]
