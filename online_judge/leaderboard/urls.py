from django.conf.urls import url
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'showleaderboard', showleaderboard),
    url(r'flushRedis', flush_RedisDB),
    url(r'', showleaderboard),
]
