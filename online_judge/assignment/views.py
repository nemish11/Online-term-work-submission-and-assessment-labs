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

@login_required()
def showWeek(request):
    try:
        c={}
        subjectid = request.POST.get('subjectid')
        subject = Subject.objects.get(pk=int(subjectid))
        all_week = Week.objects.filter(subject=subject)
        c['subject'] = subject
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
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def addweek(request):
    try:
        c = {}
        subjectid = request.POST.get('subjectid')
        weekname = request.POST.get('weekname')
        subject = Subject.objects.get(pk=int(subjectid))
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
    except:
        c = {}
        c['message'] = "Exception Occured..please try again and enter a correct details.."
        return render(request,'assignment/showWeek.html',c)

@login_required()
def new_assignment(request):
    try:
        weekid = request.POST.get('weekid')
        week = Week.objects.filter(id = int(weekid))[0]
        subject  = week.subject
        c = {}
        c['week'] = week
        c['subject'] = subject
        return render(request,'assignment/new_assignment.html',c)
    except:
        c = {}
        c['message'] = "Exception Occured..please try again and enter a correct details.."
        return render(request,'assignment/showWeek.html',c)

@login_required()
def newassignment(request):
    try:
        weekid = request.POST.get('weekid')
        title = request.POST.get('title')
        question = request.POST.get('question')
        codefile = request.FILES['codefile']
        total_inputfiles = request.POST.get('total_inputfiles')

        week = Week.objects.get(pk = int(weekid))
        subject = week.subject

        assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,deadline=datetime.now())
        assignment.save()

        assignment = Assignment.objects.filter(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question).last()
        id = assignment.id
        assignment = Assignment.objects.get(pk=int(id))

        fs = FileSystemStorage()
        dirname = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(id)

        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)

        codefilename = dirname + "/codefile.txt"
        inp = fs.save(codefilename,codefile)

        assignment_files = Assignment_files(assignment = assignment, type='codefile',filepath=codefilename,totalscore = 0)
        assignment_files.save()

        c = {}
        c['assignment'] = assignment
        c['subject'] = subject
        total_inputfile = []

        for i in range(1,int(total_inputfiles)+1):
            total_inputfile.append(str(i))

        c['total_inputfiles'] = total_inputfile
        return render(request,'assignment/add_inputfiles.html',c)
    except:
        c = {}
        c['message'] = "Exception Occured..please try again and enter a correct details.."
        return render(request,'assignment/new_assignment.html',c)

@login_required()
def uploadfiles(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        subject = assignment.subject
        total_inputfiles = assignment.total_inputfiles
        totalscore = 0

        for i in range(1,int(total_inputfiles)+1):
            inputfile = request.FILES["inputfile_"+str(i)]
            outputfile = request.FILES["outputfile_"+str(i)]
            score = request.POST.get("score_"+str(i))
            totalscore = totalscore + int(score)

            fs = FileSystemStorage()
            dirname = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(assignment.id)

            inputfilename = dirname+"/inputfile_"+str(i)+".txt"
            outputfilename = dirname+"/outputfile_"+str(i)+".txt"

            inp = fs.save(inputfilename,inputfile)
            inp = fs.save(outputfilename,outputfile)

            assignment_files = Assignment_files(assignment = assignment, type='inputfile',filepath=inputfilename,score=int(score))
            assignment_files.save()

            assignment_files = Assignment_files(assignment = assignment, type='outputfile', filepath=outputfilename, errortype='', runtime='',memoryused='')
            assignment_files.save()

        assignment.totalscore = totalscore
        assignment.save()

        c = {}
        all_week = Week.objects.filter(subject=subject)
        c['subject'] = subject
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
    except:
        c = {}
        c['message'] = "Exception Occured..please try again and enter a correct details.."
        return render(request,'assignment/add_inputfiles.html',c)

@login_required()
def showAssignment(request):
    try:
        c = {}
        assignmentid = request.POST.get('assignmentid')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        c['assignment'] = assignment

        submission = Submission.objects.filter(user = request.user,assignment = assignment).last()
        submission_files = Submission_files.objects.filter(submission = submission,type = 'codefile')

        previous_code = ''
        if submission_files:
            submission_files = submission_files[0]
            fhandler = open(BASE_DIR+"/usermodule"+submission_files.filepath,'r')
            previous_code = fhandler.read()
            fhandler.close()

        c['previous_code'] = previous_code
        return render(request,'assignment/showAssignment.html',c)
    except:
        return HttpResponseRedirect('/subject/')

    #    return render(request,'assignment/showAssignment.html',c)
@login_required()
def previous_submissions(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        user = request.user
        assignment = Assignment.objects.get(pk = int(assignmentid))
        submissions = Submission.objects.filter(user=user,assignment=assignment)

        #accepted_submissions = submissions.filter(totalscore = assignment.totalscore)
        #wrong_submissions = submissions.filter(totalscore = 0)
        accepted_submissions = submissions.filter(verdict = 'accepted')
        wrong_submissions = submissions.filter(verdict = 'wrong')
        
        c = {}
        c['assignment'] = assignment
        c['accepted'] = len(accepted_submissions)
        c['wrong'] = len(wrong_submissions)
        c['partially_accepted'] = max(0,len(submissions) - len(accepted_submissions) - len(wrong_submissions))
        c['total_submissions'] = len(submissions)
        c['submissions'] = submissions
        return render(request,'assignment/previous_submissions.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def submission_files(request):
    try:
        submissionid = request.POST.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        assignment = submission.assignment
        total_inputfiles = assignment.total_inputfiles
        submission_files = Submission_files.objects.filter(submission=submission)

        c = {}
        c['totalscore'] = submission.totalscore

        inputfiles = ["" for i in range(total_inputfiles)]
        outputfiles = ["" for i in range(total_inputfiles)]
        errorfiles = ["" for i in range(total_inputfiles)]

        codefile = submission_files.filter(filepath__contains = "/codefile")[0].filepath
        codefile_handler = open(BASE_DIR+"/usermodule"+codefile,'r')
        previous_code = codefile_handler.read()
        codefile_handler.close()

        for i in range(0,int(total_inputfiles)):
            inputfiles[i] = submission_files.filter(filepath__contains = "/input_"+str(i+1))[0]
            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))[0]
            errorfiles[i] = submission_files.filter(filepath__contains = "/error_"+str(i+1))[0]

        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)
        c['previous_code'] = previous_code
        c['assignment'] = assignment
        return render(request,'assignment/submission_files.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def submitcode(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        code = request.POST.get('code')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        subject = assignment.subject
        c = {}
        c['assignment'] = assignment
        c['subject'] = subject

        total_inputfiles = assignment.total_inputfiles
        total_inputfiles = int(total_inputfiles)

        inputfiles = ["" for i in range(total_inputfiles)]
        outputfiles = ["" for i in range(total_inputfiles)]
        errorfiles = ["" for i in range(total_inputfiles)]
        score = [0 for i in range(total_inputfiles)]

        for i in range(0,int(total_inputfiles)):
            inputfiles[i] = 'usermodule/static/all_assignment/assignment_'+str(assignment.id)+'/inputfile_'+str(i+1)+".txt"

        #submission = submit_code(request,inputfiles,outputfiles,assignment,code,total_inputfiles,errorfiles,errortypes,runtimes,memoryused,codefile)
        submission = submit_code(request,assignment,subject,inputfiles,code)
        totalscore = 0

        submission_files = Submission_files.objects.filter(submission=submission)

        for i in range(0,int(total_inputfiles)):
            assignment_outputfilepath = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(assignment.id)+"/outputfile_"+str(i+1)+".txt"

            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))[0]
            outputfilepath = BASE_DIR + "/usermodule" + outputfiles[i].filepath
            fhandler = open(outputfilepath,'r')
            data1 = fhandler.readlines()
            fhandler.close()

            fhandler = open(assignment_outputfilepath)
            data2 = fhandler.readlines()
            fhandler.close()

            #print(data1)
            #print(data2)

            assignment_file = Assignment_files.objects.filter(filepath = BASE_DIR + "/" +inputfiles[i])[0]
            if data1 == data2:
                score[i] = int(assignment_file.score)
            else:
                score[i] = 0

            totalscore = totalscore + int(score[i])

        submission.totalscore = totalscore
        if totalscore == assignment.totalscore:
            submission.verdict = "accepted"
        elif totalscore == 0:
            submission.verdict = "wrong"
        else:
            submission.verdict = "partially accepted"
        submission.save()

        c['previous_code'] = code
        c['totalscore'] = totalscore
        c['verdict'] = submission.verdict

        for i in range(0,int(total_inputfiles)):
            inputfiles[i] = submission_files.filter(filepath__contains = "/input_"+str(i+1))[0]
            inputfiles[i].score = score[i]
            inputfiles[i].save()
            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))[0]
            outputfiles[i].score = score[i]
            outputfiles[i].save()
            errorfiles[i] = submission_files.filter(filepath__contains = "/error_"+str(i+1))[0]

        #combinedlist = zip(inputfiles,outputfiles,runtimes,memoryused,errortypes,errorfiles,score)
        #c['submission_files'] = submission_files
        #c['combinedlist'] = combinedlist
        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)
        return render(request,'assignment/showAssignment.html',c)
    except:
        return HttpResponseRedirect('/subject/')
