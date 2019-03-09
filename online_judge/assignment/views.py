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
from practice.models import Problem,Problem_files,Tag
from datetime import datetime
import subprocess,threading,os,shutil
from multiprocessing import Pool
from online_judge.settings import *
from compilerApiApp.views import submit_code
import filecmp
from leaderboard.models import Leaderboard
from leaderboard.views import update_cache_week,update_cache
from django.db.models import Max,Min

@login_required()
def showWeek(request):
    try:
        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        subjectid = request.POST.get('subjectid')
        subject = Subject.objects.get(pk=int(subjectid))
        subjectyear = request.POST.get('subjectyear')
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def backtoWeek(request):
    try:
        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        subjectid = request.GET.get('subjectid')
        subject = Subject.objects.get(pk=int(subjectid))
        subjectyear = request.GET.get('subjectyear')
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def addweek(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        c = {}
        subjectid = request.POST.get('subjectid')
        subjectyear = request.POST.get('subjectyear')
        weekname = request.POST.get('weekname')
        lastdate = request.POST.get('lastdate')
        subject = Subject.objects.get(pk=int(subjectid))
        week = Week(name=weekname,subject=subject,lastdate=lastdate,year=int(subjectyear))
        week.save()
        update_cache_week(request,subjectid,week.year)
        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def deleteweek(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        weekid = request.POST.get('weekid')
        subjectid = request.POST.get('subjectid')
        subject = Subject.objects.get(pk=int(subjectid))
        subjectyear = request.POST.get('subjectyear')
        week = Week.objects.get(pk = int(weekid))
        week.isdeleted = True
        week.save()
        update_cache_week(request,subjectid,week.year)
        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def deleteAssignment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        assignmentid = request.POST.get('assignmentid')
        subjectyear = request.POST.get('subjectyear')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        subject = assignment.week.subject
        assignment.delete()
        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        messages.add_message(request, messages.WARNING, 'Some error occured..try again...!!')
        return HttpResponseRedirect('/assignment/showWeek')

@login_required()
def new_assignment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        weekid = request.POST.get('weekid')
        subjectyear = request.POST.get('subjectyear')
        week = Week.objects.get(pk = int(weekid))
        subject  = week.subject
        c = {}
        c['week'] = week
        c['subject'] = subject
        c['subjectyear'] = subjectyear
        return render(request,'assignment/new_assignment.html',c)
    except:
        return HttpResponseRedirect('/assignment/showWeek')

@login_required()
def import_assignment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        weekid = request.POST.get('weekid')
        subjectyear = request.POST.get('subjectyear')
        week = Week.objects.get(pk = int(weekid))
        subject  = week.subject
        problems = Problem.objects.all()
        c = {}
        c['week'] = week
        c['subject'] = subject
        c['subjectyear'] = subjectyear
        c['problems'] = problems
        return render(request,'assignment/import_assignment.html',c)
    except:
        return HttpResponseRedirect('/assignment/showWeek')

@login_required()
def importassignment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        weekid = request.POST.get('weekid')
        subjectyear = request.POST.get('subjectyear')
        week = Week.objects.get(pk = int(weekid))
        subject  = week.subject
        problemid = request.POST.get('problemid')
        problem = Problem.objects.get(pk = int(problemid))

        title = problem.title
        question = problem.question
        constraint = problem.constraint
        inputformat = problem.inputformat
        outputformat = problem.outputformat
        sampleinput = problem.sampleinput
        sampleoutput = problem.sampleoutput
        explanation = problem.explanation
        total_inputfiles = problem.total_inputfiles

        assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,constraint = constraint,inputformat=inputformat,outputformat=outputformat,sampleinput=sampleinput,sampleoutput=sampleoutput,explanation=explanation)
        assignment.save()

        fs = FileSystemStorage()
        dirname = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(assignment.id)

        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)

        problemcodefile = BASE_DIR + "/usermodule/static/problems/problem_"+str(problem.id)+"/codefile.txt"
        codefilename = dirname + "/codefile.txt"

        f = open(problemcodefile,'r')
        code = f.read()
        f.close()

        codefile_handler=open(codefilename,'w+')
        codefile_handler.write(code)
        codefile_handler.close()

        assignment_files = Assignment_files(assignment = assignment, type='codefile',filepath=codefilename,score = 0)
        assignment_files.save()

        totalscore = 0

        for i in range(1,int(total_inputfiles)+1):

            probleminputfile = BASE_DIR + "/usermodule/static/problems/problem_"+str(problem.id)+"/inputfile_"+str(i)+".txt"
            problemoutputfile = BASE_DIR + "/usermodule/static/problems/problem_"+str(problem.id)+"/outputfile_"+str(i)+".txt"

            dirname = BASE_DIR + "/usermodule/static/all_assignment/assignment_"+str(assignment.id)
            inputfilename = dirname+"/inputfile_"+str(i)+".txt"
            outputfilename = dirname+"/outputfile_"+str(i)+".txt"

            f = open(probleminputfile,'r')
            inputtext = f.read()
            f.close()

            inputfile_handler=open(inputfilename,'w+')
            inputfile_handler.write(inputtext)
            inputfile_handler.close()

            f = open(problemoutputfile,'r')
            outputtext = f.read()
            f.close()

            outputfile_handler=open(outputfilename,'w+')
            outputfile_handler.write(outputtext)
            outputfile_handler.close()

            problem_files = Problem_files.objects.filter(problem = problem, type="inputfile", filepath=probleminputfile)[0]
            score = problem_files.score
            totalscore = totalscore + int(score)

            assignment_files = Assignment_files(assignment = assignment, type='inputfile',filepath=inputfilename,score=int(score))
            assignment_files.save()

            assignment_files = Assignment_files(assignment = assignment, type='outputfile', filepath=outputfilename, errortype='', runtime='',memoryused='')
            assignment_files.save()

        assignment.totalscore = totalscore
        assignment.save()

        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def newassignment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        weekid = request.POST.get('weekid')
        subjectyear = request.POST.get('subjectyear')
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

        assignment = Assignment(week=week,subject=subject,total_inputfiles = int(total_inputfiles), title=title,question=question,constraint = constraint,inputformat=inputformat,outputformat=outputformat,sampleinput=sampleinput,sampleoutput=sampleoutput,explanation=explanation)
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

        c = {}
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c['min_year'] = ymin
        c['max_year'] = ymax
        all_week = Week.objects.filter(subject=subject, isdeleted=False,year=int(subjectyear))
        c['subject'] = subject
        c['all_week'] = all_week
        c['subjectyear'] = subjectyear
        all_assignment = Assignment.objects.filter(subject=subject)
        c['all_assignment'] = all_assignment
        if request.user.is_superuser:
            usertype = 'admin'
        else:
            usertype = request.user.groups.all()[0].name
        c['usertype'] = usertype
        c['faculty'] = 'faculty'
        return render(request, 'assignment/showWeek.html', c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def backtoAssignment(request):
    try:
        c = {}
        assignmentid = request.GET.get('assignmentid')
        subjectyear = request.GET.get('subjectyear')
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
        c['subjectyear'] = subjectyear
        return render(request,'assignment/showAssignment.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def showAssignment(request):
    try:
        c = {}
        assignmentid = request.POST.get('assignmentid')
        subjectyear = request.POST.get('subjectyear')
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
        c['subjectyear'] = subjectyear
        return render(request,'assignment/showAssignment.html',c)
    except:
        return HttpResponseRedirect('/subject/')

    #    return render(request,'assignment/showAssignment.html',c)
@login_required()
def previous_submissions(request):
    try:
        assignmentid = request.GET.get('assignmentid')
        subjectyear = request.GET.get('subjectyear')
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
        c['subjectyear'] = subjectyear
        return render(request,'assignment/previous_submissions.html',c)
    except:
        return HttpResponseRedirect('/subject/')


@login_required()
def submission_files(request):
    try:
        submissionid = request.POST.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        assignment = submission.assignment
        subjectyear = assignment.week.year
        total_inputfiles = assignment.total_inputfiles
        submission_files = Submission_files.objects.filter(submission=submission)

        c = {}
        c['totalscore'] = submission.totalscore
        c['submission'] = submission
        c['subjectyear'] = subjectyear
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
        c['verdict'] = submission.verdict
        return render(request,'assignment/submission_files.html',c)
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def savecomment(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        commenttext = request.POST.get('commenttext')
        submissionid = request.session.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        submission.comment = commenttext
        submission.commentunread = True
        submission.save()
        messages.add_message(request, messages.INFO, 'Comment posted sucessfully...')
        return HttpResponseRedirect('/assignment/submission_files')
    except:
        messages.add_message(request, messages.WARNING, 'SOme error occured..please try again..')
        return HttpResponseRedirect('/subject/')

@login_required()
def markcomment(request):
    try:
        if not request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/subject/')
        submissionid = request.session.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        submission.commentunread = False
        submission.save()
        messages.add_message(request, messages.INFO, 'Comment mark as read sucessfully...')
        return HttpResponseRedirect('/assignment/submission_files')
    except:
        return HttpResponseRedirect('/subject/')

@login_required()
def submitcode(request):
    try:
        assignmentid = request.POST.get('assignmentid')
        subjectyear = request.POST.get('subjectyear')
        code = request.POST.get('code')
        subjectyear = request.POST.get('subjectyear')
        assignment = Assignment.objects.get(pk = int(assignmentid))
        subject = assignment.subject
        c = {}
        c['assignment'] = assignment
        c['subject'] = subject
        c['subjectyear'] = subjectyear
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

                #print(data1)
                #print(data2)
                ldata1 = ''
                ldata2 = ''
                if data1:
                    ldata1 = data1[-1]
                    data1 = data1[:len(data1)-1]
                if data2:
                    ldata2 = data2[-1]
                    data2 = data2[:len(data2)-1]

                assignment_file = Assignment_files.objects.filter(filepath = BASE_DIR + "/" +inputfiles[i])
                if assignment_file:
                    assignment_file = assignment_file[0]
                else:
                    score[i] = 0

                if assignment_file and data1 == data2 and ldata1.strip() == ldata2.strip() and outputfiles[i].errortype == '-':
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
                update_cache(request, leaderboard)
            else:
                leaderboard = Leaderboard(subject = assignment.subject, year = studentA.year, assignment=assignment, student = studentA, week = assignment.week, maxscore = scoreA)
                leaderboard.save()
                update_cache(request, leaderboard)

        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)
        return render(request,'assignment/showAssignment.html',c)
    except:
        return HttpResponseRedirect('/subject/')


@login_required()
def studentlist_for_assignment(request):
    try:
        if request.session['usertype'] == "faculty" or request.session['usertype'] == "admin":
            year = request.POST.get('year')
            week_id = request.POST.get('week_id')
            assignment_id = request.POST.get('assignment_id')
            week = Week.objects.get(id=week_id)
            assignment = Assignment.objects.filter(id=assignment_id)[0]
            submissionlist = Submission.objects.filter(assignment=assignment).order_by('user','-datetime')
            submission_list = []
            year = int(year)
            userids = []
            for submission in submissionlist:
                student = Student.objects.filter(user = submission.user)
                if student:
                    student = student[0]
                    if int(submission.assignment.week.year) == int(year) and str(submission.user.groups.all()[0].name) == str('student') and int(submission.assignment.week.id) == int(week_id) and int(student.year) == int(year):
                        submission_list.append(submission)

            c={}
            c['submission_list'] = submission_list
            c['assignment'] = assignment
            c['week'] = week
            return render(request,'assignment/student_submission.html',c)
        else:
            return HttpResponseRedirect('/subject/')
    except:
        return HttpResponseRedirect('/assignment/showWeek')


@login_required()
def student_all_submission(request):
    try:
        if request.session['usertype'] == "faculty" or request.session['usertype'] == "admin":
            weekid = request.POST.get('weekid')
            weekid = int(weekid)
            week = Week.objects.get(id=weekid)
            userid = request.POST.get('userid')
            user = User.objects.get(id=int(userid))
            userid = int(userid)
            assignment_id= request.POST.get('assignmentid')
            assignment_id = int(assignment_id)
            assignment = Assignment.objects.get(id=assignment_id)
            submissions = Submission.objects.filter(assignment=assignment,user=user).order_by('-datetime')
            submission_list = []
            for submission in submissions:
                if submission.assignment.week.year == week.year:
                    submission_list.append(submission)
            c={}
            c['submission_list'] = submission_list
            c['week'] = week
            c['assignment'] = assignment
            c['user'] = user
            return render(request,'assignment/student_all_submission.html',c)
        else:
            return HttpResponseRedirect('/subject/')
    except:
        return HttpResponseRedirect('/assignment/showWeek')
