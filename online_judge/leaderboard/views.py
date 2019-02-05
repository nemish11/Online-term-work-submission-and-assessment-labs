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
from django.core.cache import cache
from redis import Redis
import redis
import time
from datetime import  datetime

class Connection:
    def __init__(self):
        r = Redis.StrictRedis(host='localhost', port=6379, db=0)

    def get_connection(self):
        return self.r

def initialize_leaderboard_cache(request):
    #r = Redis.Redis('default')
    r=redis.StrictRedis(host='localhost', port=6379, db=0)
    subjectid = request.session.get('leaderboard_subjectid')
    subject = Subject.objects.get(id=subjectid)
    year = 2016
    subjects = Subject.objects.filter(status=True)

    leaderboard = Leaderboard.objects.filter(year=year).values('subject', 'week', 'student').annotate(Sum('maxscore'))
    r.flushall()



    for sub in subjects:
        student_list = set()
        week_list = Week.objects.filter(subject=sub)
        for l in leaderboard:
            if l['subject'] == sub.id:
                student_list.add(l['student'])
        sname = "rank:"+str(sub.id)

        for s in student_list:
            hasname = str(sub.id)+':'+str(s)
            for w in week_list:
                wname = str(sub.id)+':'+str(s)+':'+str(w.id)
                r.hset(hasname, wname, 0)
            r.hset(sub.id, hasname, hasname)

            name = "rank:"+str(sub.id)+':'+str(s)

            r.zadd(sname,{name: 0})
        r.hset("ranklist", sname, sname)
        r.hset("leaderboard", sub.id , sub.id)

    for l in leaderboard:
        name = str(l['subject'])+':'+str(l['student'])
        key = str(l['subject'])+':'+str(l['student'])+':'+str(l['week'])
        oldval = int(r.hget(name,key))
        incre_val = l['maxscore__sum'] - oldval

        r.hincrby(name, key, incre_val)

        name_for_z = "rank:"+str(l['subject'])
        key_for_z = "rank:"+str(l['subject'])+":"+str(l['student'])
        r.zincrby(name_for_z, incre_val, key_for_z)

    return


@login_required()
def get_leaderboard(request):
    subjectid = request.session.get('leaderboard_subjectid')
    subject = Subject.objects.get(id=subjectid)
    year = 2016
    weeks = Week.objects.filter(subject=subject)
    week = {}
    for w in weeks:
        week[w.id] = w.name

    students =Student.objects.filter(year=year)
    student = {}
    for s in students:
        student[s.id] = s.user



    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    data = {}
    ranklist_data = {}

    ranklist = r.zrange("rank:"+str(subjectid),0,-1,withscores=True)
    for r in ranklist:
        r = list(r)
        key = str(r[0])
        value = r[1]
        key = list(key.split(':'))[-1]
        ranklist_data[key] = int(value)
    #print(ranklist_data)

    for r_student in r.hgetall(str(subjectid)):
        print(r_student)

        temp = r.hgetall(r_student)
        t = {}
        outer_key = list(r_student.split(':'))[-1]
        for key in temp:
            key = str(key)
            key = list(key.split(':'))[-1]
            value = int(value)
            t[key] = value
        data[outer_key] = t
    for d in data:
        print(d)
    return










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

    #leaderboard = Leaderboard.objects.values('subject', 'week', 'student').annotate(Sum('maxscore'))
    #d=datetime.now()
    #print(d.microsecond)

    leaderboard = Leaderboard.objects.filter(subject=subject,year=year).values('subject', 'student','week').annotate(Sum('maxscore'))

    #print(str(leaderboard.query))
    #leaderboard = Leaderboard.objects.values('year','subject', 'week', 'student').annotate(Sum('maxscore'))
    #d = datetime.now()
    #print(d.microsecond)

    #for l in leaderboard:
        #print(l)
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
    #initialize_leaderboard_cache(request)
    get_leaderboard(request)
    return render(request,'leaderboard/show_leaderboard.html', c)


@login_required()
def set_leaderboard_subject(request):
    try:
        subjectid = request.POST.get('subjectid')
        request.session['leaderboard_subjectid'] = subjectid
        return HttpResponseRedirect('/leaderboard/show_leaderboard')
    except:
        return HttpResponseRedirect('/subject/')

