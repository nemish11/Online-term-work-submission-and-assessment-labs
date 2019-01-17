from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    year = models.IntegerField()
    roll_no = models.CharField(max_length = 20)
    phone_no = models.CharField(max_length = 15)
    dob = models.DateField()

class Faculty(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    phone_no = models.CharField(max_length = 15)
    is_active = models.BooleanField(default = True)
