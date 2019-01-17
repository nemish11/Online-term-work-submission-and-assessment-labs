from django.db import models
from django.contrib.auth.models import User
from userprofile.models import Faculty,Student

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length = 50)
    subject_code = models.CharField(max_length = 20)
    status = models.BooleanField(default = True)

class Request(models.Model):
    faculty = models.ForeignKey(Faculty,on_delete = models.CASCADE,related_name = 'request_faculty')
    student = models.ForeignKey(Student,on_delete = models.CASCADE,related_name = 'request_student')
    subject = models.ForeignKey(Subject,on_delete = models.CASCADE,related_name = 'request_subject')
    status = models.CharField(max_length = 15)
