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


def connection():
    r = redis.StrictRedis(host=HOST, port=PORT, db=REDISDB)
    return r


'''@login_required()
def set_leaderboard_subject(request):
    try:
        r = connection()
        subjectid = request.POST.get('subjectid')
        year = request.POST.get('year')
        #year = 2016
        request.session['leaderboard_subjectid'] = subjectid
        request.session['leaderboard_year'] = year

        hash_key = str(year)+':'+str(subjectid)
        if r.exists(hash_key):
            return HttpResponseRedirect('/leaderboard/get_leaderboard')
        else:
            initialize_leaderboard_cache(request)
            return HttpResponseRedirect('/leaderboard/get_leaderboard')
    except:
        return HttpResponseRedirect('/subject/')
'''

@login_required()
def flush_RedisDB(request):
    try:
        if request.user.is_superuser or request.session['usertype'] == "faculty":
            r = connection()
            r.flushall()
            return HttpResponseRedirect('/subject/')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


def initialize_leaderboard_cache(request):
    try:
        r = connection()
        EXPIRE_TIME = 120
        subjectid = request.GET.get('subjectid')
        subject = Subject.objects.get(id=subjectid)
        year = request.GET.get('year')
        leaderboard = Leaderboard.objects.filter(subject=subject, year=year).values('subject', 'week', 'student').annotate(Sum('maxscore'))

        student_list = set()
        week_list = Week.objects.filter(subject=subject, isdeleted=False,year=int(year))
        for l in leaderboard:
            student_list.add(l['student'])
        subject_rank_name = "rank:"+str(year)+':'+str(subjectid)
        for s in student_list:
            subject_hash_key = str(year)+':'+str(subjectid)+':'+str(s)
            for w in week_list:
                student_hash_key = str(year)+':'+str(subjectid)+':'+str(s)+':'+str(w.id)
                r.hset(subject_hash_key, student_hash_key, 0)
                r.expire(student_hash_key,EXPIRE_TIME)
            r.hset(str(year)+':'+str(subjectid), subject_hash_key, subject_hash_key)

            name = "rank:"+str(year)+':'+str(subjectid)+':'+str(s)
            r.zadd(subject_rank_name,{name: 0})
            r.expire(subject_rank_name,EXPIRE_TIME)
            r.expire(subject_hash_key,EXPIRE_TIME)
        r.hset("ranklist", subject_rank_name, subject_rank_name)
        r.hset("leaderboard", str(year)+':'+str(subjectid), str(year)+':'+str(subjectid))

        r.expire(subject_rank_name, EXPIRE_TIME)
        r.expire(str(year)+':'+str(subjectid), EXPIRE_TIME)

        for l in leaderboard:
            name = str(year)+':'+str(l['subject'])+':'+str(l['student'])
            key = str(year)+':'+str(l['subject'])+':'+str(l['student'])+':'+str(l['week'])
            name = str(name)
            key = str(key)
            oldval = int(r.hget(name, key))
            incre_val = l['maxscore__sum'] - oldval

            r.hincrby(name, key, incre_val)

            name_for_z = "rank:"+str(year)+':'+str(l['subject'])
            key_for_z = "rank:"+str(year)+':'+str(l['subject'])+":"+str(l['student'])
            r.zincrby(name_for_z, incre_val, key_for_z)

        return
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def showleaderboard(request):
    try:
        r = connection()
        subjectid = request.GET.get('subjectid')
        subject = Subject.objects.get(id=subjectid)
        year = request.GET.get('year')

        hash_key = str(year) + ':' + str(subjectid)
        if not r.exists(hash_key):
            initialize_leaderboard_cache(request)

        weeks = Week.objects.filter(subject=subject, isdeleted=False,year=int(year))
        week = {}
        for w in weeks:
            week[w.id] = w.name

        students =Student.objects.filter(year=year)
        student = {}
        for s in students:
            student[str(s.id)] = s.user.username


        data = {}
        ranklist_data = {}

        #d = datetime.now()
        #print(d.microsecond)

        ranklist = r.zrevrange("rank:"+str(year)+':'+str(subjectid), 0, -1, withscores=True)
        for ra in ranklist:
            ra = list(ra)
            key = str(ra[0])
            value = ra[1]
            key = list(key.split(':'))[-1]
            key = str(key)
            key = key[:len(key)-1]
            ranklist_data[key] = int(value)

        subject_key = str(year)+':'+str(subjectid)
        for r_student in r.hgetall(subject_key):

            temp = r.hgetall(r_student)
            t = {}
            outer_key = list(str(r_student).split(':'))[-1]
            outer_key = outer_key[:len(outer_key)-1]
            for key in temp:
                value = temp[key]
                key = str(key)
                key = list(key.split(':'))[-1]
                key = key[:len(key)-1]

                value = int(value)
                t[key] = value
            data[outer_key] = t

        data_leaderboard = {}
        count =1
        for key in ranklist_data:
            temp_dic={}
            temp_dic['student_name'] = student[key]
            temp_dic['totalscore'] = ranklist_data[key]

            student_dic = data[key]
            for student_d in student_dic:
                temp_dic[student_d] = student_dic[student_d]
            data_leaderboard[count] = temp_dic
            count += 1

        #d = datetime.now()
        #print(d.microsecond)
        c = {}
        c['subject'] = subject
        c['data'] = data_leaderboard
        c['weeks'] = week
        c['students'] = student
        c['ranklist'] = ranklist_data

        return render(request,'leaderboard/leaderboard.html', c)
    except:
        messages.add_message(request, messages.WARNING, 'something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


def update_cache(request,leaderboard):
    try:
        r = connection()
        student_id = leaderboard.student.id
        subject_id = leaderboard.subject.id
        week_id = leaderboard.week.id
        year = leaderboard.year
        key = str(year)+':'+str(subject_id)+":"+str(student_id)+":"+str(week_id)
        name = str(year)+':'+str(subject_id)+":"+str(student_id)
        oldval = int(r.hget(name, key))
        incre_val = leaderboard.maxscore - oldval
        r.hincrby(name, key, incre_val)
        name_for_z = "rank:"+str(year)+':' + str(subject_id)
        key_for_z = "rank:" + str(year)+':' + str(subject_id) + ":" + str(student_id)
        r.zincrby(name_for_z, incre_val, key_for_z)

        return
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


def update_cache_week(request,subjectid,year):
    try:
        r = connection()

        hash_key = str(year)+':'+str(subjectid)
        set_key = "rank:"+str(year)+':'+str(subjectid)
        if r.exists(hash_key):
            r.expire(hash_key, 10)
        if r.exists(set_key):
            r.expire(set_key, 10)

        return
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def show_leaderboard(request):
    try:
        subjectid = request.session.get('leaderboard_subjectid')
        subject = Subject.objects.get(id=subjectid)
        year = 2016
        weeks = Week.objects.filter(subject=subject)
        week_dic = {}
        for week in weeks:
            week_dic[week.id] = week.name
        c = {}
        leaderboard = Leaderboard.objects.filter(subject=subject,year=year).values('subject', 'student','week').annotate(Sum('maxscore'))
        students = Leaderboard.objects.filter(subject=subject, year=year)
        # print(leaderboard)
        leaderboard_data = {}

        for student1 in students:
            t={}

            t['name'] = student1.student.user
            t['total'] = 0
            for week in weeks:
                t[week.id] = 0
            leaderboard_data[student1.student.id] = t
        for l in leaderboard:
            if int(l['subject']) == int(subjectid):
                leaderboard_data[l['student']][l['week']] = l['maxscore__sum']
                leaderboard_data[l['student']]['total'] += l['maxscore__sum']
        data = dict(sorted(leaderboard_data.items(), key=lambda x: x[1]['total'], reverse=True))
        c={}
        c['leaderboard_data'] = data
        c['subject'] = subject
        c['weeks'] = week_dic
        #d = datetime.now()
        #print(d.microsecond)

        return render(request, 'leaderboard/show_leaderboard.html', c)
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')
