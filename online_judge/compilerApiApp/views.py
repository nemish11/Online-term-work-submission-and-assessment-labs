from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Submissions_all,Submissions_all_files
from online_judge.settings import *
from django.core.files.storage import FileSystemStorage
import subprocess,threading
import os,shutil
from multiprocessing import Pool

# Create your views here.

def program_file(request):
    return render(request,'compilerApiApp/index.html')

def run_input_files(request,counter,dirname,c,fs,filename,submission,inputfiles,outputfiles,errorfiles,errortypes,runtimes,memoryused,language):

    inputfile = inputfiles[counter-1]
    fhandler = open(inputfile,'r')
    inputfiledata = fhandler.read()
    fhandler.close()

    inputfile_handler = open(dirname+"/input_"+str(counter)+".txt",'w+')
    inputfile_handler.write(inputfiledata)
    inputfile_handler.close()
    #inp = fs.save(dirname+"/input_"+str(counter)+".txt",inputfile)
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

    code = request.POST.get('code','')
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

    if (language == 'c' or language == 'C' or language == 'C++' or language == 'c++'):
        if os.stat(errorfilename).st_size != 0:
            input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='compile error',runtime='0.0',memoryused='-')
            input_f.save()
            output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='compile error',runtime='0.0',memoryused='-')
            output_f.save()
            fhandler = open(errorfilename,'r')
            errortypes[counter-1] = "compile error"
            c['message'] = "compiler error " + fhandler.read(400)
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
                    input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Time OUT',runtime='2.0',memoryused='-')
                    input_f.save()
                    output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Time OUT',runtime='2.0',memoryused='-')
                    output_f.save()
                    c['message'] ="Time OUT" + data[index:index+31]
                else:
                    errortypes[counter-1] = 'runtime error'
                    input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                    input_f.save()
                    output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                    output_f.save()
                    c['message'] ="runtime error" + data[index:index+31]
            else:
                c['message'] = "sucessfully run"

                index = int(data.find("Command"))
                f = open(outputfilename,"w")
                f.write(data[0:index-1])
                f.close()

                time_taken = int(data.find("User time (seconds)"))
                time_taken1 = data[time_taken+20:time_taken+25] + "sec"
                runtimes[counter-1] = time_taken1
                c['time_taken'] =  time_taken1

                memory_used = int(data.find("Maximum resident set size (kbytes)"))
                memory_used1 = ""
                pointer = memory_used + 36

                while data[pointer]!='\n':
                    memory_used1 = memory_used1 + data[pointer]
                    pointer = pointer + 1

                memory_used1 = memory_used1 + "kb"
                memoryused[counter-1] = memory_used1
                c['memory_used'] = memory_used1

                input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                input_f.save()

                output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                output_f.save()

    elif language == 'python' or language == 'Python':

        fhandler = open(errorfilename,'r')
        data = fhandler.read()
        fhandler.close()

        index = int(data.find("Traceback"))

        if index != -1: #runtime error
            input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='runtime error',runtime='0.0',memoryused='-')
            input_f.save()
            output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='runtime error',runtime='0.0',memoryused='-')
            output_f.save()
            fhandler = open(errorfilename,'r')
            errortypes[counter-1] = "runtime error"
            index = int(data.find("Command"))
            errormessage = fhandler.read(index)
            c['message'] = "runtime error " + errormessage
            fhandler.close()

        else:
            index = int(data.find("Command terminated by signal"))
            termination_code = -1

            if (index != -1): #timeout or other error
                termination_code = data[index+29:index+30]

                if termination_code == "9":
                    errortypes[counter-1] = 'Time OUT'
                    input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Time OUT',runtime='2.0',memoryused='-')
                    input_f.save()
                    output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Time OUT',runtime='2.0',memoryused='-')
                    output_f.save()
                    c['message'] ="Time OUT" + data[index:index+31]
                else:
                    errortypes[counter-1] = 'runtime error'
                    input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                    input_f.save()
                    output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                    output_f.save()
                    c['message'] ="runtime error" + data[index:index+31]

            else: #successfully run
                c['message'] = "sucessfully run"

                time_taken = int(data.find("User time (seconds)"))
                time_taken1 = data[time_taken+20:time_taken+25] + "sec"
                runtimes[counter-1] = time_taken1
                c['time_taken'] =  time_taken1

                memory_used = int(data.find("Maximum resident set size (kbytes)"))
                memory_used1 = ""
                pointer = memory_used + 36

                while data[pointer]!='\n':
                    memory_used1 = memory_used1 + data[pointer]
                    pointer = pointer + 1

                memory_used1 = memory_used1 + "kb"
                memoryused[counter-1] = memory_used1
                c['memory_used'] = memory_used1

                input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                input_f.save()

                output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
                output_f.save()

    else:
        return "NO langauage available"


def submit_code(request,inputfiles,outputfiles,username,language,code,inputfilecount,errorfiles,errortypes,runtimes,memoryused,codefile):
    c = {}
    submission = Submissions_all(username=username,language=language,datetime=datetime.now(),isRunning='YES')
    submission.save()
    submission = Submissions_all.objects.filter(username=username,isRunning='YES',language=language).last()
    id = submission.id
    submission = Submissions_all.objects.get(pk=int(id))

    fs = FileSystemStorage()
    filename = BASE_DIR + "/compilerApiApp/all_submissions/"
    dirname = filename + str(id)

    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname)

    counter = 1
    #inputfilecount = 3#request.POST.get['inputfilecount']
    if language == 'c' or language == 'C':
        codefile[0] = dirname + "/codefile.c"
    elif language == 'C++' or language == 'c++':
        codefile[0] = dirname + "/codefile.cpp"
    elif language == 'python' or language == 'Python':
        codefile[0] = dirname + "/codefile.py"
        #print('codefile : ',codefile[0])
    else:
        return "NO language supported"

    #print(codefile[0])
    codefile_handler=open(codefile[0],'w')
    codefile_handler.write(code)
    codefile_handler.close()

    code_file_object = Submissions_all_files(type='codefile',submission=submission,filepath=codefile[0],errortype='-',runtime='-',memoryused='-')
    code_file_object.save()

    thread_arr = []

    while counter <= inputfilecount :
        thread_arr.append(str(counter))
        thread_arr[counter-1] = threading.Thread(target=run_input_files,args=(request,counter,dirname,c,fs,filename,submission,inputfiles,outputfiles,errorfiles,errortypes,runtimes,memoryused,language,))
        thread_arr[counter-1].start()
        counter = counter + 1

    counter1=1
    while counter1 <= inputfilecount:
        thread_arr[counter1-1].join()
        counter1 = counter1 + 1

    submission.isRunning = 'NO'
    submission.save()
    return "sucess"
