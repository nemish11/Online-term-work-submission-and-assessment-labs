
from django.conf.urls import url
from django.urls import path
from usermodule.views import login

urlpatterns = [
    url(r'login',login),
]
