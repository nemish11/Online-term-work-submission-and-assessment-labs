from django.db import models
from django.contrib.auth.models import User
from subject.models import Subject
# Create your models here.

class Week(models.Model):
    subject = models.ForeignKey(Subject,on_delete = models.CASCADE,related_name = 'week_subject')
    name = models.CharField(max_length = 20)
    is_locked = models.BooleanField(default = False)

class Assignment(models.Model):
    week = models.ForeignKey(Week,on_delete = models.CASCADE,related_name = 'assignment_week')
    title = models.CharField(max_length = 100)
    question = models.CharField(max_length = 1000)
    deadline = models.DateField()

class Assignment_files(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignmentfiles_assignment')
    type = models.CharField(max_length = 20)
    errortype = models.CharField(max_length=100,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=20,null=True)
    filepath = models.CharField(max_length = 100)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submission_user')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submission_assignment')
    score = models.IntegerField()
    status = models.CharField(max_length = 20)

class Submission_files(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submissionfiles_submission')
    type = models.CharField(max_length = 20)
    errortype = models.CharField(max_length=100,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=20,null=True)
    filepath = models.CharField(max_length = 100)
