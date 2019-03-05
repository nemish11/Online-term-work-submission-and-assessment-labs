from django.db import models
from subject.models import Subject
from assignment.models import Assignment,Week
from userprofile.models import Student
#  Create your models here.
import uuid

class Leaderboard(models.Model):
    #id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='leaderboard_subject')
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE,related_name='leaderboard_assignment')
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='leaderboard_student')
    week = models.ForeignKey(Week,on_delete=models.CASCADE,related_name='leaderboard_week')
    year = models.IntegerField()
    maxscore = models.IntegerField(default = 0)

    def __str__(self):
        return (str(self.subject.name+' '+self.student.user.username+' '+str(self.maxscore)+' '+self.week.name))
