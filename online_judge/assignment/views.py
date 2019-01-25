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
from assignment.models import Week,Submission,Assignment,Assignment_files,Submission_files
from datetime import datetime
import subprocess,threading,os,shutil
from multiprocessing import Pool
from online_judge.settings import *
from compilerApiApp.views import submit_code
import filecmp

def showWeek(request):
    c={}
    subject = Subject.objects.get(pk=int(1))
    all_week = Week.objects.filter(subject=subject)
    c['all_week'] = all_week
    all_assignment = Assignment.objects.filter(subject=subject)
    c['all_assignment'] = all_assignment
    if request.user.is_superuser:
        usertype = 'admin'
    else:
        usertype = request.user.groups.all()[0].name
    c['usertype'] = usertype
    c['faculty'] = 'faculty'
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
    if request.user.is_superuser:
        usertype = 'admin'
    else:
        usertype = request.user.groups.all()[0].name
    c['usertype'] = usertype
    c['faculty'] = 'faculty'
    return render(request,'assignment/showWeek.html',c)

def new_assignment(request):
    id = request.POST.get('weekid')
    week = Week.objects.filter(id = int(id))[0]
    c = {}
    c['week'] = week
    return render(request,'assignment/new_assignment.html',c)

def newassignment(request):
    id = request.POST.get('weekid')
    title = request.POST.get('title')
    question = request.POST.get('question')
    codefile = request.FILES['codefile']
    total_inputfiles = request.POST.get('total_inputfiles')

    week = Week.objects.filter(id = int(id))[0]
    subject = Subject.objects.all()[0]

    assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,deadline=datetime.now())
    assignment.save()

    assignment = Assignment.objects.filter(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question).last()
    id = assignment.id
    assignment = Assignment.objects.get(pk=int(id))

    fs = FileSystemStorage()
    dirname = BASE_DIR + "/assignment/all_files/all_assignment/assignment_"+str(id)

    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname)

    codefilename = dirname + "/codefile.txt"
    inp = fs.save(codefilename,codefile)

    assignment_files = Assignment_files(assignment = assignment, type='codefile',filepath=codefilename)
    assignment_files.save()

    c = {}
    c['assignment'] = assignment
    total_inputfile = []

    for i in range(1,int(total_inputfiles)+1):
        total_inputfile.append(str(i))

    c['total_inputfiles'] = total_inputfile
    return render(request,'assignment/add_inputfiles.html',c)

def uploadfiles(request):
    id = request.POST.get('assignmentid')
    assignment = Assignment.objects.filter(id = int(id))[0]
    total_inputfiles = assignment.total_inputfiles

    for i in range(1,int(total_inputfiles)+1):
        inputfile = request.FILES["inputfile_"+str(i)]
        outputfile = request.FILES["outputfile_"+str(i)]
        score = request.POST.get("score_"+str(i))

        fs = FileSystemStorage()
        dirname = BASE_DIR + "/assignment/all_files/all_assignment/assignment_"+str(assignment.id)

        inputfilename = dirname+"/inputfile_"+str(i)+".txt"
        outputfilename = dirname+"/outputfile_"+str(i)+".txt"

        inp = fs.save(inputfilename,inputfile)
        inp = fs.save(outputfilename,outputfile)

        assignment_files = Assignment_files(assignment = assignment, type='inputfile',filepath=inputfilename,score=score)
        assignment_files.save()

        assignment_files = Assignment_files(assignment = assignment, type='outputfile', filepath=outputfilename, errortype='', runtime='',memoryused='')
        assignment_files.save()

    return HttpResponseRedirect('/assignment/showWeek')

def showAssignment(request):
    c = {}
    id = request.POST.get('assignmentid')
    assignment = Assignment.objects.filter(id = int(id))[0]
    c['assignment'] = assignment

    try:
        submission = Submission.objects.filter(user = request.user,assignment = assignment).last()
        submission_files = Submission_files.objects.filter(submission = submission,type = 'codefile')[0]

        fhandler = open(submission_files.filepath,'r')
        previous_code = fhandler.read()
        fhandler.close()

        c['previous_code'] = previous_code
        return render(request,'assignment/showAssignment.html',c)
    except:
        return render(request,'assignment/showAssignment.html',c)

def submitcode(request):
    assignmentid = request.POST.get('assignmentid')
    code = request.POST.get('code')
    assignment = Assignment.objects.filter(id = int(assignmentid))[0]
    subject = assignment.subject
    c = {}
    c['assignment'] = assignment
    c['subject'] = subject

    total_inputfiles = assignment.total_inputfiles
    total_inputfiles = int(total_inputfiles)

    inputfiles = ["" for i in range(total_inputfiles)]
    outputfiles = ["" for i in range(total_inputfiles)]
    errorfiles = ["" for i in range(total_inputfiles)]
    errortypes = ["" for i in range(total_inputfiles)]
    runtimes = ["" for i in range(total_inputfiles)]
    memoryused = ["" for i in range(total_inputfiles)]
    score = [0 for i in range(total_inputfiles)]
    codefile = [""]

    for i in range(0,int(total_inputfiles)):
        inputfiles[i] = 'assignment/all_files/all_assignment/assignment_'+str(assignment.id)+'/inputfile_'+str(i+1)+".txt"

    username = request.user.username
    language = 'python'

    submission = Submission(user=request.user,assignment=assignment,datetime=datetime.now(),isrunning='YES')
    output = submit_code(request,inputfiles,outputfiles,username,language,code,total_inputfiles,errorfiles,errortypes,runtimes,memoryused,codefile)

    c['outputfiles'] = outputfiles
    c['errortypes'] = errortypes
    c['errorfiles'] = errorfiles
    c['runtimes'] = runtimes
    c['memoryused'] = memoryused

    #print(errortypes)
    #print(runtimes)
    #print(memoryused)
    totalscore = 0
    for i in range(0,int(total_inputfiles)):
        assignment_outputfilepath = BASE_DIR + "/assignment/all_files/all_assignment/assignment_"+str(assignment.id)+"/outputfile_"+str(i+1)+".txt"

        fhandler = open(outputfiles[i],'r')
        data1 = fhandler.readlines()
        fhandler.close()

        fhandler = open(assignment_outputfilepath)
        data2 = fhandler.readlines()
        fhandler.close()

        print(data1)
        print(data2)

        if data1 == data2:
            score[i] = 5
        else:
            score[i] = 0

        totalscore = totalscore + int(score[i])

    submission.totalscore = totalscore
    submission.save()

    submission_files = Submission_files(submission=submission,type='codefile',score=int(totalscore),filepath=codefile[0])
    submission_files.save()

    for i in range(0,int(total_inputfiles)):
        submission_files = Submission_files(submission=submission,type='inputfile',score=int(score[i]),runtime=runtimes[i],errortype=errortypes[i],memoryused=memoryused[i],filepath=inputfiles[i])
        submission_files.save()

        submission_files = Submission_files(submission=submission,type='outputfile',score=int(score[i]),runtime=runtimes[i],errortype=errortypes[i],memoryused=memoryused[i],filepath=outputfiles[i])
        submission_files.save()

    c['previous_code'] = code
    c['totalscore'] = totalscore
    return render(request,'assignment/showAssignment.html',c)
