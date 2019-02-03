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
    subjectid = request.session.get('leaderboard_subjectid')
    subject = Subject.objects.get(id=subjectid)
    year = 2016
    weeks = Week.objects.filter(subject=subject)
    week_dic = {}
    for week in weeks:
        week_dic[week.id] = week.name
    c = {}
    leaderboard = Leaderboard.objects.values('subject', 'week', 'student').annotate(Sum('maxscore'))
    students = Leaderboard.objects.filter(subject=subject,year=year)
    # print(leaderboard)
    leaderboard_data = {}

    for student1 in students:
        t={}

        t['name'] = student1.student.user
        t['total'] = 0
        for week in weeks:
            t[week.id] = 0
        leaderboard_data[student1.student.id] = t
    #print(leaderboard)
    for l in leaderboard:
        if int(l['subject']) == int(subjectid):
            leaderboard_data[l['student']][l['week']] = l['maxscore__sum']
            leaderboard_data[l['student']]['total'] += l['maxscore__sum']
    #print(leaderboard_data)
    data = dict(sorted(leaderboard_data.items(), key=lambda x: x[1]['total'], reverse=True))
    #print(data)
    c={}
    c['leaderboard_data'] = data
    c['subject'] = subject
    c['weeks'] = week_dic
    return render(request,'leaderboard/show_leaderboard.html', c)


@login_required()
def set_leaderboard_subject(request):

        subjectid = request.POST.get('subjectid')
        print(subjectid)
        request.session['leaderboard_subjectid'] = subjectid
        return HttpResponseRedirect('/leaderboard/show_leaderboard')

        return HttpResponseRedirect('/subject/')

def tearDown(self):
    from django_redis import get_redis_connection
    get_redis_connection("default").flushall()