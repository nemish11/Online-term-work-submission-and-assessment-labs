from django.conf.urls import url
from django.urls import path
from .views import home

urlpatterns = [
    url(r'',home),
]
