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

@login_required()
def allstudents(request):
    try:
        c = {}
        allstudents = Student.objects.all()
        c['allstudents'] = allstudents
        return render(request,'searchuser/allstudents.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def fullprofile(request):
    try:
        studentid = request.POST.get('studentid')
        student = Student.objects.get(pk = int(studentid))
        c = {}
        accepted_submissions = Submission.objects.filter(user = student.user, verdict = "accepted")
        wrong_submissions = Submission.objects.filter(user = student.user, verdict = "wrong")
        partially_accepted_submissions = Submission.objects.filter(user = student.user, verdict = "partially accepted")
        c['student'] = student
        c['accepted'] = len(accepted_submissions)
        c['wrong'] = len(wrong_submissions)
        c['partially_accepted'] = len(partially_accepted_submissions)
        c['total_submissions'] = len(accepted_submissions) + len(wrong_submissions) + len(partially_accepted_submissions)
        return render(request,'searchuser/fullprofile.html',c)
    except:
        return HttpResponseRedirect('/searchuser/')

@login_required()
def sortby(request):
    try:
        year = request.POST.get('selectedyear')
        students = Student.objects.filter(year = int(year))
        c = {}
        c['students'] = students
        return render(request,'searchuser/sortby.html',c)
    except:
        c = {}
        c['message'] = "Exception Occured..please enter a correct details.."
        allstudents = Student.objects.all()
        c['allstudents'] = allstudents
        return render(request,'searchuser/allstudents.html',c)
