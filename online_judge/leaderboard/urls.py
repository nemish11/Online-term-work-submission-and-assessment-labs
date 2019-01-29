from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [

    url(r'show_leaderboard', show_leaderboard),
    url(r'', show_leaderboard),

]