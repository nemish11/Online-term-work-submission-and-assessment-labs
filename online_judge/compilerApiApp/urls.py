from django.conf.urls import url
from django.urls import path
from compilerApiApp.views import program_file,submit_code

urlpatterns = [
    url(r'submitcode',submit_code),
    url(r'',program_file),
    #url(r'^index/$',dummy),
]
