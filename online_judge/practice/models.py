from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Problem(models.Model):
    title = models.TextField()
    question = models.TextField(blank=True,null=True)
    constraint = models.TextField(null=True,blank=True)
    inputformat = models.TextField(null=True,blank=True)
    outputformat = models.TextField(null=True,blank=True)
    sampleinput = models.TextField(null=True,blank=True)
    sampleoutput = models.TextField(null=True,blank=True)
    explanation = models.TextField(null=True,blank=True)
    total_inputfiles = models.IntegerField(default=0)
    totalscore = models.IntegerField(default=0)
    accuracy = models.FloatField(default=None)
    difficulty = models.CharField(max_length = 30)
    successful_submission = models.IntegerField(default=0)
    total_submission = models.IntegerField(default = 0)
    tags = models.CharField(max_length=200,null=True,blank=True)
    isdeleted = models.BooleanField(default=False)

class Tag(models.Model):
    name = models.TextField()
    problems = models.ManyToManyField(Problem)

class Problem_files(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='problemfiles_problem')
    type = models.CharField(max_length = 100)
    score = models.IntegerField(default=0)
    errortype = models.CharField(max_length=1000,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=50,null=True)
    filepath = models.TextField()

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Submission_user')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submission_problem')
    totalscore = models.IntegerField(default=0)
    language = models.CharField(max_length = 30)
    datetime = models.DateTimeField(null=True,blank=True)
    verdict = models.CharField(max_length = 50,null=True)
    isrunning = models.CharField(max_length = 20)
    comment = models.TextField(null=True,blank=True)
    commentunread = models.BooleanField(default = True,null=True,blank=True)

class Submission_files(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='submissionfiles_submission')
    type = models.CharField(max_length = 20)
    score = models.IntegerField(default=0)
    errortype = models.CharField(max_length=1000,null=True)
    runtime = models.CharField(max_length=20,null=True)
    memoryused = models.CharField(max_length=50,null=True)
    filepath = models.TextField()
