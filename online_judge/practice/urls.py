from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'allproblems',all_problems),
    url(r'filterproblems',filter_problems),
    url(r'add_problem',add_problem),
    url(r'addproblem',addproblem),
    url(r'add_tag',add_tag),
    url(r'addtag',addtag),
    url(r'removeproblem',removeproblem),
    url(r'showproblem',showproblem),
    url(r'problem/$',showproblem),
    url(r'previous_submissions/$',previous_submissions),
    url(r'runcode',runcode),
    url(r'',all_problems),
]
