from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib import messages
import pandas as pd
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import pandas as pd
from userprofile.models import Faculty,Student
from subject.models import Subject
from assignment.models import Week,Submission,Assignment,Assignment_files
import datetime

def showWeek(request):
    c={}
    subject = Subject.objects.get(pk=int(1))
    all_week = Week.objects.filter(subject=subject)
    c['all_week'] = all_week
    all_assignment = Assignment.objects.filter(subject=subject)
    c['all_assignment'] = all_assignment
    return render(request,'assignment/showWeek.html',c)

def addweek(request):
    c = {}
    weekname = request.POST.get('weekname')
    subject = Subject.objects.get(pk=int(1))
    week = Week(name=weekname,subject=subject)
    week.save()
    all_week = Week.objects.filter(subject=subject)
    c['all_week'] = all_week
    all_assignment = Assignment.objects.filter(subject=subject)
    c['all_assignment'] = all_assignment
    return render(request,'assignment/showWeek.html',c)

def new_assignment(request):
    return render(request,'assignment/new_assignment.html')

def newassignment(request):
    title = request.POST.get('title')
    question = request.POST.get('question')
    total_inputfiles = request.POST.get('total_inputfiles')
    week = Week.objects.all()[0]
    subject = Subject.objects.all()[0]
    assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,deadline=datetime.date.today())
    assignment.save()
    c = {}
    c['assignment'] = assignment
    total_inputfile = []

    for i in range(1,int(total_inputfiles)+1):
        total_inputfile.append(str(i))

    c['total_inputfiles'] = total_inputfile
    return render(request,'assignment/add_inputfiles.html',c)

def uploadfiles(request):
    id = request.GET.get('id')
    
    return HttpResponseRedirect('/assignment/showWeek')

def showAssignment(request):
    c = {}
    id = request.GET.get('id')
    assignment = Assignment.objects.filter(id = int(id))[0]
    c['title'] = assignment.title
    c['question'] = assignment.question
    return render(request,'assignment/showAssignment.html',c)
