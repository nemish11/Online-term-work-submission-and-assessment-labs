from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'show_leaderboard',show_leaderboard),
    url(r'',show_leaderboard),
]
