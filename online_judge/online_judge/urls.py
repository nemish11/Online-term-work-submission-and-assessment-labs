"""online_judge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include,url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^subject/',include('subject.urls')),
    url(r'^usermodule/',include('usermodule.urls')),
    url(r'userprofile/',include('userprofile.urls')),
    url(r'compilerApiApp/',include('compilerApiApp.urls')),
    url(r'assignment/',include('assignment.urls')),
    url(r'searchuser/',include('searchuser.urls')),
    url(r'leaderboard/',include('leaderboard.urls')),
    url(r'practice/',include('practice.urls')),
    url(r'',include('usermodule.urls')),
]
