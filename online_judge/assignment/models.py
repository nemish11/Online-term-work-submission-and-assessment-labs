from django.db import models
from django.contrib.auth.models import User
from subject.models import Subject
import uuid
# Create your models here.

class Week(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject,on_delete = models.CASCADE,related_name = 'week_subject')
    year = models.IntegerField()
    name = models.CharField(max_length = 50)
    isdeleted = models.BooleanField(default=False)
    lastdate = models.DateField()

class Assignment(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week = models.ForeignKey(Week,on_delete = models.CASCADE,related_name = 'assignment_week')
    subject = models.ForeignKey(Subject,on_delete = models.CASCADE,related_name = 'assignment_subject',null=True,blank=True)
    title = models.TextField()
    totalscore = models.IntegerField(default=0)
    isdeleted = models.BooleanField(default=False)
    question = models.TextField(blank=True,null=True)
    constraint = models.TextField(null=True,blank=True)
    inputformat = models.TextField(null=True,blank=True)
    outputformat = models.TextField(null=True,blank=True)
    sampleinput = models.TextField(null=True,blank=True)
    sampleoutput = models.TextField(null=True,blank=True)
    explanation = models.TextField(null=True,blank=True)
    total_inputfiles = models.IntegerField(default = 0)

class Assignment_files(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignmentfiles_assignment')
    type = models.CharField(max_length = 100)
    score = models.IntegerField(default=0)
    errortype = models.CharField(max_length=1000,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=50,null=True)
    filepath = models.TextField()

class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submission_user')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submission_assignment')
    totalscore = models.IntegerField(default=0)
    datetime = models.DateTimeField()
    verdict = models.CharField(max_length = 50,null=True)
    isrunning = models.CharField(max_length = 20)
    comment = models.TextField(null=True,blank=True)
    commentunread = models.BooleanField(default = True)

class Submission_files(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submissionfiles_submission')
    type = models.CharField(max_length = 20)
    score = models.IntegerField(default=0)
    errortype = models.CharField(max_length=1000,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=50,null=True)
    filepath = models.TextField()
