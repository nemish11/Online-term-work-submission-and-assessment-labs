from django.shortcuts import render
from django.shortcuts import render,render_to_response
from django.template.context_processors import csrf
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from assignment.models import Week,Assignment,Submission
from subject.models import Subject,Request
#from .models import *
from userprofile.models import Faculty, Student

@login_required()
def show_leaderboard(request):
    subject = Subject.objects.all().first()
    weeks = Week.objects.filter(subject=subject)
    students = Request.objects.filter(subject=subject, status="approved")
    submision_list = Submission.objects.all()
    dic = {}
    for s in students:
        dic[s.student.user] = {}
        t = {}
        t['total_score'] = 0
        for w in weeks:
            t[w.name] = 0
        dic[s.student.user] = t
    '''for key in dic:
        d = dic[key]
        for w in weeks:

            assign = Assignment.objects.filter(week=w, subject=subject,Submission__user=request.user).sum('totalscore')

            d[w.name] = assign
            print(key.user.username, w.name, assign)'''
    for s in submision_list:
        assign = s.assignment
        w = assign.week.name
        if dic[s.user][w] > s.totalscore and assign.subject == subject:
            dic[s.user]['total_score'] -= dic[s.user][w] + s.totalscore
            dic[s.user][w] = s.totalscore

    c = {}
    c['data'] = dic
    c['weeks'] = weeks
    c['subject'] = subject
    return render(request, 'leaderboard/show_leaderboard.html', c)




