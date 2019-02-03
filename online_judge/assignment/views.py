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
from leaderboard.models import Leaderboard

@login_required()
def showWeek(request):
        c={}
        subjectid = request.session.get('subjectid')
        subject = Subject.objects.get(pk=int(subjectid))
        all_week = Week.objects.filter(subject=subject,isdeleted=False)
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
        #return HttpResponseRedirect('/subject/')

@login_required()
def addweek(request):
    try:
        c = {}
        subjectid = request.session.get('subjectid')
        weekname = request.POST.get('weekname')
        subject = Subject.objects.get(pk=int(subjectid))
        week = Week(name=weekname,subject=subject)
        week.save()
        return HttpResponseRedirect('/assignment/showWeek')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def deleteweek(request):
    try:
        weekid = request.POST.get('weekid')
        week = Week.objects.get(pk = int(weekid))
        week.isdeleted = True
        week.save()
        return HttpResponseRedirect('/assignment/showWeek')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def deleteAssignment(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        assignment.delete()
        return HttpResponseRedirect('/assignment/showWeek')
    except:
        messages.add_message(request, messages.WARNING, 'Some error occured..try again...!!')
        return HttpResponseRedirect('/assignment/showWeek')

@login_required()
def new_assignment(request):
    try:
        weekid = request.POST.get('weekid')
        week = Week.objects.get(pk = int(weekid))
        subject  = week.subject
        c = {}
        c['week'] = week
        c['subject'] = subject
        return render(request,'assignment/new_assignment.html',c)
    except:
        return HttpResponseRedirect('/assignment/showWeek')

@login_required()
def newassignment(request):
    try:
        weekid = request.POST.get('weekid')
        title = request.POST.get('title')
        question = request.POST.get('question')
        constraint = request.POST.get('constraint')
        inputformat = request.POST.get('inputformat')
        outputformat = request.POST.get('outputformat')
        sampleinput = request.POST.get('sampleinput')
        sampleoutput = request.POST.get('outputformat')
        explanation = request.POST.get('explanation')

        codefile = request.FILES['codefile']
        total_inputfiles = request.POST.get('total_inputfiles')

        week = Week.objects.get(pk = int(weekid))
        subject = week.subject

        assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,constraint = constraint,inputformat=inputformat,outputformat=outputformat,sampleinput=sampleinput,sampleoutput=sampleoutput,explanation=explanation,deadline=datetime.now())
        assignment.save()

        fs = FileSystemStorage()
        dirname = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(assignment.id)

        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)

        codefilename = dirname + "/codefile.txt"
        inp = fs.save(codefilename,codefile)

        assignment_files = Assignment_files(assignment = assignment, type='codefile',filepath=codefilename,score = 0)
        assignment_files.save()

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

        return HttpResponseRedirect('/assignment/showWeek')
    except:
        return HttpResponseRedirect('/subject/')

'''
@login_required()
def addinputfiles(request):
    c = {}
    assignmentid = request.session.get('addassignmentid')
    subjectid = request.session.get('subjectid')
    assignment = Assignment.objects.get(pk = int(assignmentid))
    subject = Subject.objects.get(pk = int(subjectid))
    c['assignment'] = assignment
    c['subject'] = subject
    total_inputfiles = assignment.total_inputfiles
    total_inputfile = []

    for i in range(1,int(total_inputfiles)+1):
        total_inputfile.append(str(i))

    c['total_inputfiles'] = total_inputfile
    return render(request,'assignment/add_inputfiles.html',c)

@login_required()
def uploadfiles(request):
        assignmentid = request.session.get('addassignmentid')
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

        return HttpResponseRedirect('/assignment/showWeek')
        return HttpResponseRedirect('/subject/')'''

@login_required()
def selectedAssignment(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        request.session['assignmentid'] = assignmentid
        return HttpResponseRedirect('/assignment/showAssignment')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def showAssignment(request):
    try:
        c = {}
        assignmentid = request.session.get('assignmentid')
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
        assignmentid = request.session.get('assignmentid')
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
def selectedsubmission(request):
    try:
        submissionid = request.POST.get('submissionid')
        request.session['submissionid'] = submissionid
        return HttpResponseRedirect('/assignment/submission_files')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def submission_files(request):
    try:
        submissionid = request.session.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        assignment = submission.assignment
        total_inputfiles = assignment.total_inputfiles
        submission_files = Submission_files.objects.filter(submission=submission)

        c = {}
        c['totalscore'] = submission.totalscore

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
        return render(request,'assignment/submission_files.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def runcode(request):
    try:
        code = request.POST.get('code')
        request.session['assignmentcode'] = code
        return HttpResponseRedirect('/assignment/submitcode')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def submitcode(request):

        assignmentid = request.session.get('assignmentid')
        code = request.session.get('assignmentcode')
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

            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))

            if outputfiles[i]:
                outputfiles[i] = outputfiles[i][0]
                outputfilepath = BASE_DIR + "/usermodule" + outputfiles[i].filepath
                fhandler = open(outputfilepath,'r')
                data1 = fhandler.readlines()
                fhandler.close()

                fhandler = open(assignment_outputfilepath)
                data2 = fhandler.readlines()
                fhandler.close()

                ldata1 = data1[-1]
                data1 = data1[:len(data1)-1]
                ldata2 = data2[-1]
                data2 = data2[:len(data2)-1]

                assignment_file = Assignment_files.objects.filter(filepath = BASE_DIR + "/" +inputfiles[i])[0]
                '''if assignment_file:
                    assignment_file = assignment_file[i][0]
                else:
                    score[i] = 0'''

                if assignment_file and data1 == data2 and ldata1.strip() == ldata2.strip():
                    score[i] = int(assignment_file.score)
                else:
                    score[i] = 0
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
            inputfiles[i] = submission_files.filter(filepath__contains = "/input_"+str(i+1))
            if inputfiles[i]:
                inputfiles[i] = inputfiles[i][0]
                inputfiles[i].score = score[i]
                inputfiles[i].save()
            else:
                c['message'] = "file properly not uploaded..please contact to faculty"
            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))
            if outputfiles[i]:
                outputfiles[i] = outputfiles[i][0]
                outputfiles[i].score = score[i]
                outputfiles[i].save()
            else:
                c['message'] = "file properly not uploaded..please contact to faculty"
            errorfiles[i] = submission_files.filter(filepath__contains = "/error_"+str(i+1))
            if errorfiles[i]:
                errorfiles[i] = errorfiles[i][0]
            else:
                c['message'] = "file properly not uploaded..please contact to faculty"

        #combinedlist = zip(inputfiles,outputfiles,runtimes,memoryused,errortypes,errorfiles,score)
        #c['submission_files'] = submission_files
        #c['combinedlist'] = combinedlist
        if request.user.groups.all()[0].name == 'student':
            scoreA = sum(score)
            studentA = Student.objects.filter(user = request.user)[0]
            leaderboard = Leaderboard.objects.filter(student  = studentA, year = studentA.year, subject = assignment.subject, assignment = assignment, week = assignment.week)
            if leaderboard:
                leaderboard = leaderboard[0]
                leaderboard.maxscore = max(leaderboard.maxscore,scoreA)
                leaderboard.save()
            else:
                leaderboard = Leaderboard(subject = assignment.subject, year = studentA.year, assignment=assignment, student = studentA, week = assignment.week, maxscore = scoreA)
                leaderboard.save()

        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)
        return render(request,'assignment/showAssignment.html',c)

        return HttpResponseRedirect('/subject/')
