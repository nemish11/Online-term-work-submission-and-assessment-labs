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
def selectedstudent(request):
    try:
        studentid = request.POST.get('studentid')
        request.session['selectedstudentfp'] = studentid
        return HttpResponseRedirect('/searchuser/fullprofile')
    except:
        messages.add_message(request, messages.WARNING, 'some error occured..please try again..!!')
        return HttpResponseRedirect('/searchuser/')

@login_required()
def fullprofile(request):
    try:
        studentid = request.session.get('selectedstudentfp')
        student = Student.objects.get(pk = int(studentid))
        c = {}
        all_submissions = Submission.objects.filter(user = student.user)
        accepted_submissions = all_submissions.filter(verdict = "accepted")
        wrong_submissions = all_submissions.filter(verdict = "wrong")
        partially_accepted_submissions = all_submissions.filter(verdict = "partially accepted")
        c['student'] = student
        c['accepted'] = len(accepted_submissions)
        c['wrong'] = len(wrong_submissions)
        c['partially_accepted'] = len(partially_accepted_submissions)
        c['total_submissions'] = len(all_submissions)
        return render(request,'searchuser/fullprofile.html',c)
    except:
        messages.add_message(request, messages.WARNING, 'some error occured..please try again..!!')
        return HttpResponseRedirect('/searchuser/')

@login_required()
def allsubmissions(request):
    try:
        studentid = request.session.get('selectedstudentfp')
        student = Student.objects.get(pk = int(studentid))
        c = {}
        all_submissions = Submission.objects.filter(user = student.user)
        c['submissions'] = all_submissions
        return render(request,'searchuser/all_submissions.html',c)
    except:
        return HttpResponseRedirect('/searchuser/')

@login_required()
def sortedstudent(request):
    try:
        year = request.session.get('sortbyyear')
        students = Student.objects.filter(year = int(year))
        c = {}
        c['students'] = students
        messages.add_message(request, messages.INFO, 'below listed sorted student!!!')
        return render(request,'searchuser/sortby.html',c)
    except:
        messages.add_message(request, messages.WARNING, 'Some Error occured..please try again..!!')
        return HttpResponseRedirect('/searchuser/')

@login_required()
def sortby(request):
    try:
        year = request.POST.get('selectedyear')
        request.session['sortbyyear'] = year
        return HttpResponseRedirect('/searchuser/sortedstudent')
    except:
        messages.add_message(request, messages.WARNING, 'please enter a correct details..!!')
        return HttpResponseRedirect('/searchuser/')
