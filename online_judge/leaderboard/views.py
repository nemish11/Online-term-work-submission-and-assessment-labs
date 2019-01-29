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
    students = Request.objects.filter(subject=subject,status="approved")
    dic = {}
    for s in students:
        dic[s.student] = {}
    for key in dic:
        d = dic[key]
        for w in weeks:

            assign = Assignment.objects.filter(week=w, subject=subject,Submission__user=request.user).sum('totalscore')

            d[w.name] = assign
            print(key.user.username, w.name, assign)
    c={}
    c['data'] = dic
    c['weeks'] = weeks
    c['subject'] = subject
    return render(request, 'leaderboard/show_leaderboard.html', c)




