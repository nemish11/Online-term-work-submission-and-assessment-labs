from django.db import models
from django.contrib.auth.models import User
import uuid

class Student(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    year = models.IntegerField()
    roll_no = models.CharField(max_length = 30)
    phone_no = models.CharField(max_length = 15)
    dob = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default = True)


class Faculty(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    phone_no = models.CharField(max_length = 15)
    dob = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default = True)
