from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'set_leaderboard_subject', set_leaderboard_subject),
    url(r'get_leaderboard', get_leaderboard),
    url(r'flushRedis', flush_RedisDB),
    url(r'', get_leaderboard),
]
