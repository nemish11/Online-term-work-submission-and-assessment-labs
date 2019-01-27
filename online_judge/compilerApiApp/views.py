from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
import pandas as pd
from datetime import datetime
from django.utils import timezone
from assignment.models import Submission,Submission_files
from online_judge.settings import *
from django.core.files.storage import FileSystemStorage
import subprocess,threading
import os,shutil
from multiprocessing import Pool

# Create your views here.

def program_file(request):
    return render(request,'compilerApiApp/index.html')

def run_input_files(request,counter,dirname,submission,inputfiles,outputfiles,errorfiles,errortypes,runtimes,memoryused,language,code,filename):

    inputfile = inputfiles[counter-1]
    fhandler = open(inputfile,'r')
    inputfiledata = fhandler.read()
    fhandler.close()

    inputfile_handler = open(dirname+"/input_"+str(counter)+".txt",'w+')
    inputfile_handler.write(inputfiledata)
    inputfile_handler.close()

    outputfile_handler = open(dirname+"/output_"+str(counter)+".txt",'w+')
    outputfile_handler.close()

    errorfile_handler = open(dirname+"/error_"+str(counter)+".txt",'w+')
    errorfile_handler.close()

    inputfilename = dirname+"/input_"+str(counter)+".txt"
    outputfilename = dirname+"/output_"+str(counter)+".txt"
    errorfilename = dirname+"/error_"+str(counter)+".txt"

    outputfiles[counter-1] = outputfilename
    errorfiles[counter-1] = errorfilename
    errortypes[counter-1] = '-'
    runtimes[counter-1] = '-'
    memoryused[counter-1] = '-'

    codefile = ''

    if language == 'c' or language == 'C':
        codefile = dirname + "/codefile_"+str(counter)+".c"
    elif language == 'C++' or language == 'c++':
        codefile = dirname + "/codefile_"+str(counter)+".cpp"
    elif language == 'python' or language == 'Python':
        codefile = dirname + "/codefile_"+str(counter)+".py"
    else:
        return "NO language supported"

    codefile_handler=open(codefile,'w+')
    codefile_handler.write(code)
    codefile_handler.close()

    if language == 'c' or language == 'C':
        tmp = subprocess.call([filename+"./c_run.sh", codefile, dirname+"/codefile_"+str(counter)+".out", dirname+"/./codefile_"+str(counter)+".out", inputfilename,outputfilename, errorfilename])
    elif language == 'C++' or language == 'c++':
        tmp = subprocess.call([filename+"./cpp_run.sh", codefile, dirname+"/codefile_"+str(counter)+".out", dirname+"/./codefile_"+str(counter)+".out", inputfilename,outputfilename, errorfilename])
    elif language == 'python' or language == 'Python':
        tmp = subprocess.call([filename+"./py_run.sh", codefile, inputfilename,outputfilename, errorfilename])
    else:
        return "No language supported"

    #tmp = subprocess.call([filename+"./run.sh", codefile, dirname+"/codefile_"+str(counter)+".out", dirname+"/./codefile_"+str(counter)+".out", inputfilename,outputfilename, dirname+"/error.txt"])
    if os.path.exists(codefile):
        os.remove(codefile)

    if os.path.exists(dirname+"/codefile_"+str(counter)+".out"):
        os.remove(dirname+"/codefile_"+str(counter)+".out")

    inputfilepath = int(inputfilename.find('/static'))
    inputfilepath = inputfilename[inputfilepath:]
    outputfilepath = int(outputfilename.find('/static'))
    outputfilepath = outputfilename[outputfilepath:]
    errorfilepath = int(errorfilename.find('/static'))
    errorfilepath = errorfilename[errorfilepath:]

    if (language == 'c' or language == 'C' or language == 'C++' or language == 'c++'):
        if os.stat(errorfilename).st_size != 0:
            input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='compile error',runtime='0.0',memoryused='-')
            input_f.save()
            output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='compile error',runtime='0.0',memoryused='-')
            output_f.save()
            error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='compile error',runtime='0.0',memoryused='-')
            error_f.save()
            fhandler = open(errorfilename,'r')
            errortypes[counter-1] = "compile error"
            #c['message'] = "compiler error " + fhandler.read(400)
            fhandler.close()

        else:

            f = open(outputfilename,'r')
            data = f.read()
            f.close()

            index = int(data.find("Command terminated by signal"))
            termination_code = -1

            if index != -1:
                termination_code = data[index+29:index+30]
                index = int(data.find("Command"))
                f = open(outputfilename,"w")
                f.write(data[0:index-1])
                f.close()

                if termination_code == "9":
                    errortypes[counter-1] = 'Time OUT'
                    input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    input_f.save()
                    output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    output_f.save()
                    error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    error_f.save()
                    #c['message'] ="Time OUT" + data[index:index+31]
                else:
                    errortypes[counter-1] = 'runtime error'
                    input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    input_f.save()
                    output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    output_f.save()
                    error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    error_f.save()
                    #c['message'] ="runtime error" + data[index:index+31]
            else:
                #c['message'] = "sucessfully run"

                index = int(data.find("Command"))
                f = open(outputfilename,"w")
                f.write(data[0:index-1])
                f.close()

                time_taken = int(data.find("User time (seconds)"))
                time_taken1 = data[time_taken+20:time_taken+25] + "sec"
                runtimes[counter-1] = time_taken1
                #c['time_taken'] =  time_taken1

                memory_used = int(data.find("Maximum resident set size (kbytes)"))
                memory_used1 = ""
                pointer = memory_used + 36

                while data[pointer]!='\n':
                    memory_used1 = memory_used1 + data[pointer]
                    pointer = pointer + 1

                memory_used1 = memory_used1 + "kb"
                memoryused[counter-1] = memory_used1
                #c['memory_used'] = memory_used1

                input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                input_f.save()

                output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                output_f.save()

                error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='-r',runtime=str(time_taken1),memoryused=str(memory_used1))
                error_f.save()

    elif language == 'python' or language == 'Python':

        fhandler = open(errorfilename,'r')
        data = fhandler.read()
        fhandler.close()

        index = int(data.find("Command being timed"))
        index1 = int(data.find("Command terminated by signal"))

        if index != 1 and index1==-1: #runtime error
            input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='runtime error',runtime='0.0',memoryused='-')
            input_f.save()
            output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='runtime error',runtime='0.0',memoryused='-')
            output_f.save()
            error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='runtime error',runtime='0.0',memoryused='-')
            error_f.save()
            fhandler = open(errorfilename,'r')
            errortypes[counter-1] = "runtime error"
            index = int(data.find("Command"))
            errormessage = fhandler.read(index)
            #c['message'] = "runtime error " + errormessage
            fhandler.close()

        else:
            index = int(data.find("Command terminated by signal"))
            termination_code = -1

            if (index != -1): #timeout or other error
                termination_code = data[index+29:index+30]
                if termination_code == "9":
                    errortypes[counter-1] = 'Time OUT'
                    runtimes[counter-1] = '2.01 sec'
                    input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    input_f.save()
                    output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    output_f.save()
                    error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='Time OUT',runtime='2.0',memoryused='-')
                    error_f.save()
                #    c['message'] ="Time OUT" + data[index:index+31]
                else:
                    errortypes[counter-1] = 'runtime error'
                    runtime[counter-1] = '0.00 sec'
                    input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    input_f.save()
                    output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    output_f.save()
                    error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='Runtime error',runtime='0.0',memoryused='-')
                    error_f.save()
                #    c['message'] ="runtime error" + data[index:index+31]

            else: #successfully run
                #c['message'] = "sucessfully run"
                time_taken = int(data.find("User time (seconds)"))
                time_taken1 = data[time_taken+20:time_taken+25] + "sec"
                runtimes[counter-1] = time_taken1
                #c['time_taken'] =  time_taken1

                memory_used = int(data.find("Maximum resident set size (kbytes)"))
                memory_used1 = ""
                pointer = memory_used + 36

                while data[pointer]!='\n':
                    memory_used1 = memory_used1 + data[pointer]
                    pointer = pointer + 1

                memory_used1 = memory_used1 + "kb"
                memoryused[counter-1] = memory_used1
                #c['memory_used'] = memory_used1

                input_f = Submission_files(type='inputfile',submission=submission,filepath=inputfilepath,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                input_f.save()

                output_f = Submission_files(type='outputfile',submission=submission,filepath=outputfilepath,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                output_f.save()

                error_f = Submission_files(type='errorfile',submission=submission,filepath=errorfilepath,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                error_f.save()

    else:
        return "NO langauage available"


def submit_code(request,assignment,subject,inputfiles,code):
    submission = Submission(user=request.user,assignment=assignment,datetime=datetime.now(),isrunning='YES')
    submission.save()
    submission = Submission.objects.filter(user=request.user,isrunning='YES',assignment=assignment).last()
    id = submission.id
    submission = Submission.objects.get(pk=int(id))

    fs = FileSystemStorage()
    filename = BASE_DIR + "/usermodule/static/all_submissions/"
    dirname = filename + str(id)

    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname)

    counter = 1
    language = assignment.subject.name
    codefile = ''
    #inputfilecount = 3#request.POST.get['inputfilecount']
    if language == 'c' or language == 'C':
        codefile = dirname + "/codefile.c"
    elif language == 'C++' or language == 'c++':
        codefile = dirname + "/codefile.cpp"
    elif language == 'python' or language == 'Python':
        codefile = dirname + "/codefile.py"
        #print('codefile : ',codefile[0])
    else:
        return "NO language supported"

    codefile_handler=open(codefile,'w')
    codefile_handler.write(code)
    codefile_handler.close()

    codefilepath = int(codefile.find('/static'))
    codefilepath = codefile[codefilepath:]

    code_file_object = Submission_files(type='codefile',submission=submission,filepath=codefilepath,errortype='-',runtime='-',memoryused='-')
    code_file_object.save()

    thread_arr = []

    total_inputfiles = assignment.total_inputfiles

    outputfiles = ["" for i in range(total_inputfiles)]
    errorfiles = ["" for i in range(total_inputfiles)]
    errortypes = ["" for i in range(total_inputfiles)]
    runtimes = ["" for i in range(total_inputfiles)]
    memoryused = ["" for i in range(total_inputfiles)]
    score = [0 for i in range(total_inputfiles)]

    while counter <= total_inputfiles :
        thread_arr.append(str(counter))
        thread_arr[counter-1] = threading.Thread(target=run_input_files,args=(request,counter,dirname,submission,inputfiles,outputfiles,errorfiles,errortypes,runtimes,memoryused,language,code,filename))
        thread_arr[counter-1].start()
        counter = counter + 1

    counter1=1
    while counter1 <= total_inputfiles :
        thread_arr[counter1-1].join()
        counter1 = counter1 + 1

    submission.isrunning = 'NO'
    submission.save()
    return submission,outputfiles,errorfiles,errortypes,runtimes,memoryused,score
