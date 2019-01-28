from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'fullprofile',fullprofile),
    url(r'allstudents',allstudents),
    url(r'sortby',sortby),
    url(r'',allstudents),
]
