from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from userprofile.models import Faculty,Student
from subject.models import Subject
from assignment.models import Week,Submission,Assignment,Assignment_files,Submission_files
from datetime import datetime
from online_judge.settings import *
from .models import Leaderboard
from django.db.models import *

@login_required()
def show_leaderboard(request):
    subject = Subject.objects.get(id = int(1))
    year = 2016

    c = {}
    leaderboard = Leaderboard.objects.values('subject', 'week', 'student').annotate(Sum('maxscore'))
    # print(leaderboard)
    for l in leaderboard:
        print(l)

    return HttpResponseRedirect('/subject/')
