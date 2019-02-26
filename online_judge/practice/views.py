from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import pandas as pd
from userprofile.models import Faculty,Student
from .models import *
from datetime import datetime
import subprocess,threading,os,shutil
from multiprocessing import Pool
from online_judge.settings import *
from .utils import submit_code
import filecmp
from leaderboard.models import Leaderboard


@login_required()
def all_problems(request):
    try:
        c = {}
        problems = Problem.objects.all()
        c['problems'] = problems
        return render(request,'practice/all_problems.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def filter_problems(request):
    try:
        c = {}
        return render(request,'practice/filtered_problems.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def add_problem(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        c = {}
        tags = Tag.objects.all()
        c['tags'] = tags
        return render(request,'practice/add_problem.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def add_tag(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        return render(request,'practice/addtag.html')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def addtag(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        tagname = request.POST.get('tagname','')
        tag = Tag(name = tagname)
        tag.save()
        return HttpResponseRedirect('/practice/add_problem')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def removeproblem(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        problemid = request.POST.get('problemid')
        Problem.objects.get(pk = int(problemid)).delete()
        return HttpResponseRedirect('/practice/')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def showproblem(request):
    try:
        problemid = request.GET.get('id')
        problem = Problem.objects.get(pk = int(problemid))
        request.session['problemid'] = problemid
        submission = Submission.objects.filter(user = request.user,problem = problem).last()
        submission_files = Submission_files.objects.filter(submission = submission,type = 'codefile')

        previous_code = ''
        if submission_files:
            submission_files = submission_files[0]
            fhandler = open(BASE_DIR+"/usermodule"+submission_files.filepath,'r')
            previous_code = fhandler.read()
            fhandler.close()

        c = {}
        c['previous_code'] = previous_code
        c['problem'] = problem
        return render(request,'practice/showproblem.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def previous_submissions(request):
    try:
        problemid = request.GET.get('id')
        problem = Problem.objects.get(pk=int(problemid))
        submissions = Submission.objects.filter(user = request.user,problem=problem)
        accepted_submissions = submissions.filter(verdict = 'accepted')
        wrong_submissions = submissions.filter(verdict = 'wrong')
        c = {}
        c['submissions'] = submissions
        c['problem'] = problem
        c['accepted'] = len(accepted_submissions)
        c['wrong'] = len(wrong_submissions)
        c['partially_accepted'] = max(0,len(submissions) - len(accepted_submissions) - len(wrong_submissions))
        c['total_submissions'] = len(submissions)
        return render(request,'practice/previous_submissions.html',c)
    except:
        return HttpResponseRedirect('/practice/')


def selectedsubmission(request):
    try:
        submissionid = request.POST.get('submissionid')
        request.session['submissionid'] = submissionid
        return HttpResponseRedirect('/practice/submission_files')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def submission_files(request):
    try:
        submissionid = request.session.get('submissionid')
        submission = Submission.objects.get(pk=int(submissionid))
        problem = submission.problem
        total_inputfiles = problem.total_inputfiles
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

        c['problem'] = problem
        return render(request,'practice/submission_files.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def filter_problems(request):
    try:
        c = {}
        tags = Tag.objects.all()
        c['tags'] = tags
        return render(request,'practice/filterproblems.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def filterproblems(request):
    try:
        difficulty = request.POST.getlist('difficulty[]')
        problemtags = request.POST.getlist('problemtags[]')
        request.session['selected_difficulty'] = difficulty
        request.session['selected_problemtags'] = problemtags
        return HttpResponseRedirect('/practice/selectedproblems')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def selectedproblems(request):
    try:
        difficulty = request.session.get('selected_difficulty')
        problemtags = request.session.get('selected_problemtags')
        problems = Problem.objects.filter(difficulty__in = difficulty)
        for tag in problemtags:
            problems = problems | Problem.objects.filter(tags__contains = tag)
        c = {}
        c['problems'] = problems
        return render(request,'practice/all_problems.html',c)
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def addproblem(request):
    try:
        if request.session.get('usertype') == 'student':
            return HttpResponseRedirect('/admin/')
        title = request.POST.get('title')
        question = request.POST.get('question')
        constraint = request.POST.get('constraint')
        inputformat = request.POST.get('inputformat')
        outputformat = request.POST.get('outputformat')
        sampleinput = request.POST.get('sampleinput')
        sampleoutput = request.POST.get('outputformat')
        explanation = request.POST.get('explanation')
        difficulty = request.POST.get('difficulty')
        problemtags = request.POST.getlist('problemtags[]')
        codefile = request.FILES['codefile']
        total_inputfiles = request.POST.get('total_inputfiles')

        problem = Problem(title=title,question=question,constraint=constraint,inputformat=inputformat,outputformat=outputformat,
                sampleinput=sampleinput,sampleoutput=sampleoutput,explanation=explanation,difficulty=difficulty,
                total_inputfiles=total_inputfiles,accuracy='0.0')
        problem.save()

        for problemtag in problemtags:
            tag = Tag.objects.filter(name = problemtag)[0]
            tag.problems.add(problem)
            tag.save()
        tags = problem.tag_set.all()
        ctags = ''
        for tag in tags:
            ctags = ctags + tag.name + ','
        problem.tags = ctags[0:len(ctags)-1]
        problem.save()
        fs = FileSystemStorage()
        dirname = BASE_DIR + "/usermodule/static/problems/problem_"+str(problem.id)

        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)

        codefilename = dirname + "/codefile.txt"
        inp = fs.save(codefilename,codefile)

        problem_files = Problem_files(problem=problem, type='codefile',filepath=codefilename,score = 0)
        problem_files.save()

        totalscore = 0

        for i in range(1,int(total_inputfiles)+1):
            inputfile = request.FILES["inputfile_"+str(i)]
            outputfile = request.FILES["outputfile_"+str(i)]
            score = request.POST.get("score_"+str(i))
            totalscore = totalscore + int(score)

            fs = FileSystemStorage()

            inputfilename = dirname+"/inputfile_"+str(i)+".txt"
            outputfilename = dirname+"/outputfile_"+str(i)+".txt"

            inp = fs.save(inputfilename,inputfile)
            inp = fs.save(outputfilename,outputfile)

            problem_files = Problem_files(problem=problem, type='inputfile',filepath=inputfilename,score=int(score))
            problem_files.save()

            problem_files = Problem_files(problem=problem, type='outputfile', filepath=outputfilename, errortype='', runtime='',memoryused='')
            problem_files.save()

        problem.totalscore = totalscore
        problem.save()

        return HttpResponseRedirect('/practice/')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def runcode(request):
    try:
        code = request.POST.get('code')
        language = request.POST.get('language')
        request.session['selected_language'] = language
        request.session['problemcode'] = code
        return HttpResponseRedirect('/practice/submitcode')
    except:
        return HttpResponseRedirect('/practice/')


@login_required()
def submitcode(request):
    try:
        problemid = request.session.get('problemid')
        code = request.session.get('problemcode')
        language = request.session.get('selected_language')
        problem = Problem.objects.get(pk = int(problemid))
        c = {}
        c['problem'] = problem

        total_inputfiles = problem.total_inputfiles
        total_inputfiles = int(total_inputfiles)

        inputfiles = ["" for i in range(total_inputfiles)]
        outputfiles = ["" for i in range(total_inputfiles)]
        errorfiles = ["" for i in range(total_inputfiles)]
        score = [0 for i in range(total_inputfiles)]

        for i in range(0,int(total_inputfiles)):
            inputfiles[i] = 'usermodule/static/problems/problem_'+str(problem.id)+'/inputfile_'+str(i+1)+".txt"

        #submission = submit_code(request,inputfiles,outputfiles,assignment,code,total_inputfiles,errorfiles,errortypes,runtimes,memoryused,codefile)
        submission = submit_code(request,problem,inputfiles,code,language)
        totalscore = 0

        submission_files = Submission_files.objects.filter(submission=submission)

        for i in range(0,int(total_inputfiles)):
            problem_outputfilepath = BASE_DIR + "/usermodule/static/problems/problem_"+str(problem.id)+"/outputfile_"+str(i+1)+".txt"

            outputfiles[i] = submission_files.filter(filepath__contains = "/output_"+str(i+1))

            if outputfiles[i]:
                outputfiles[i] = outputfiles[i][0]
                outputfilepath = BASE_DIR + "/usermodule" + outputfiles[i].filepath
                fhandler = open(outputfilepath,'r')
                data1 = fhandler.readlines()
                fhandler.close()

                fhandler = open(problem_outputfilepath)
                data2 = fhandler.readlines()
                fhandler.close()

                ldata1 = ''
                ldata2 = ''
                if data1:
                    ldata1 = data1[-1]
                    data1 = data1[:len(data1)-1]
                if data2:
                    ldata2 = data2[-1]
                    data2 = data2[:len(data2)-1]

                problem_file = Problem_files.objects.filter(filepath = BASE_DIR + "/" +inputfiles[i])
                if problem_file:
                    problem_file = problem_file[0]
                else:
                    score[i] = 0

                if problem_file and data1 == data2 and ldata1.strip() == ldata2.strip():
                    score[i] = int(problem_file.score)
                else:
                    score[i] = 0
            else:
                score[i] = 0

            totalscore = totalscore + int(score[i])

        submission.totalscore = totalscore
        if totalscore == problem.totalscore:
            submission.verdict = "accepted"
        elif totalscore == 0:
            submission.verdict = "wrong"
        else:
            submission.verdict = "partially accepted"
        submission.save()

        problem.total_submission = (int(problem.total_submission) + 1)
        problem.save()
        if submission.verdict == "accepted":
            submission_x = Submission.objects.filter(problem = problem,user = request.user,verdict="accepted")
            if (not submission_x) or (submission_x[0] == submission):
                problem.successful_submission = (int(problem.successful_submission) + 1)
        problem.accuracy = round((problem.successful_submission/problem.total_submission)*100,2)
        problem.save()
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

        c['combinedlist'] = zip(inputfiles,outputfiles,errorfiles)
        return render(request,'practice/showproblem.html',c)
    except:
        return HttpResponseRedirect('/practice/')
