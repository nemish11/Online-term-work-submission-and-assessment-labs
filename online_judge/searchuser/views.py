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
        #print(request.session.get('usertype'))
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        c = {}
        allstudents = Student.objects.all()
        c['allstudents'] = allstudents
        return render(request,'searchuser/allstudents.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def selectedstudent(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        studentid = request.POST.get('studentid')
        request.session['selectedstudentfp'] = studentid
        return HttpResponseRedirect('/searchuser/fullprofile')
    except:
        messages.add_message(request, messages.WARNING, 'some error occured..please try again..!!')
        return HttpResponseRedirect('/searchuser/')

@login_required()
def fullprofile(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
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
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
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
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
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
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        year = request.POST.get('selectedyear')
        request.session['sortbyyear'] = year
        return HttpResponseRedirect('/searchuser/sortedstudent')
    except:
        messages.add_message(request, messages.WARNING, 'please enter a correct details..!!')
        return HttpResponseRedirect('/searchuser/')

@login_required()
def selectedsubmission(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        submissionid = request.POST.get('submissionid')
        request.session['submissionid'] = submissionid
        return HttpResponseRedirect('/searchuser/submission_files')
    except:
        return HttpResponseRedirect('/subject/')


@login_required()
def submission_files(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        submissionid = request.session.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        assignment = submission.assignment
        total_inputfiles = assignment.total_inputfiles
        submission_files = Submission_files.objects.filter(submission=submission)

        c = {}
        c['totalscore'] = submission.totalscore
        c['submission'] = submission
        c['true'] = True

        inputfiles = ["" for i in range(total_inputfiles)]
        outputfiles = ["" for i in range(total_inputfiles)]
        errorfiles = ["" for i in range(total_inputfiles)]

        codefile = submission_files.filter(filepath__contains = "/codefile")
        if codefile:
            codefile = codefile[0].filepath
            codefile_handler = open(BASE_DIR+"/usermodule"+codefile,'r')
            previous_code = codefile_handler.read()
            c['previous_code'] = previous_code
            codefile_handler.close()
        else:
            c['message'] = 'file properly not uploaded..please contact to faculty.'

        for i in range(0,int(total_inputfiles)):
            inputfiles[i] = submission_files.filter(filepath__contains = "/input_"+str(i+1))
            if inputfiles[i]:
                inputfiles[i] = inputfiles[i][0]
            else:
                c['message'] = 'file properly not uploaded..please contact to faculty.'
            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))
            if outputfiles[i]:
                outputfiles[i] = outputfiles[i][0]
            else:
                c['message'] = 'file properly not uploaded..please contact to faculty.'
            errorfiles[i] = submission_files.filter(filepath__contains = "/error_"+str(i+1))
            if errorfiles[i]:
                errorfiles[i] = errorfiles[i][0]
            else:
                c['message'] = 'file properly not uploaded..please contact to faculty.'

        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)

        c['assignment'] = assignment
        return render(request,'searchuser/submission_files.html',c)
    except:
        return HttpResponseRedirect('/subject/')
