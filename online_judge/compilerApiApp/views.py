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

def run_input_files(request,counter,dirname,c,fs,filename,submission):
    inputfile = request.FILES["inputfile_"+str(counter)]
    inp = fs.save(dirname+"/input_"+str(counter)+".txt",inputfile)

    outputfile_handler = open(dirname+"/output_"+str(counter)+".txt",'w+')
    outputfile_handler.close()

    errorfile_handler = open(dirname+"/error.txt",'w+')
    errorfile_handler.close()

    inputfilename = dirname+"/input_"+str(counter)+".txt"
    outputfilename = dirname+"/output_"+str(counter)+".txt"

    code = request.POST.get('code','')
    codefile = dirname + "/codefile_"+str(counter)+".cpp"
    codefile_handler=open(codefile,'w+')
    codefile_handler.write(code)
    codefile_handler.close()

    tmp = subprocess.call([filename+"./run.sh", codefile, dirname+"/codefile_"+str(counter)+".out", dirname+"/./codefile_"+str(counter)+".out", inputfilename,outputfilename, dirname+"/error.txt"])

    if os.path.exists(codefile):
        os.remove(codefile)

    if os.path.exists(dirname+"/codefile_"+str(counter)+".out"):
        os.remove(dirname+"/codefile_"+str(counter)+".out")

    if os.stat(dirname+"/error.txt").st_size != 0:
        input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='compiler error',runtime='0.0',memoryused='-')
        input_f.save()
        output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='compiler error',runtime='0.0',memoryused='-')
        output_f.save()
        fhandler = open(dirname+"/error.txt",'r')
        c['message'] = "compiler error " + fhandler.read(400)

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
            f.write(data[0:index])
            f.close()

            if termination_code == "9":
                input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Time OUT',runtime='2.0',memoryused='-')
                input_f.save()
                output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Runtime error',runtime='2.0',memoryused='-')
                output_f.save()
                c['message'] ="Time OUT" + data[index:index+31]
            else:
                input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                input_f.save()
                output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='Runtime error',runtime='0.0',memoryused='-')
                output_f.save()
                c['message'] ="runtime error" + data[index:index+31]
        else:
            c['message'] = "sucessfully run"

            index = int(data.find("Command"))
            f = open(outputfilename,"w")
            f.write(data[0:index])
            f.close()

            time_taken = int(data.find("User time (seconds)"))
            time_taken1 = data[time_taken+20:time_taken+25] + "sec"
            c['time_taken'] =  time_taken1

            memory_used = int(data.find("Maximum resident set size (kbytes)"))
            memory_used1 = data[memory_used+36:memory_used+41] +"kb"
            c['memory_used'] = memory_used1

            input_f = Submissions_all_files(type='inputfile',submission=submission,filepath=inputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
            input_f.save()

            output_f = Submissions_all_files(type='outputfile',submission=submission,filepath=outputfilename,errortype='-',runtime=str(time_taken1),memoryused=str(memory_used1))
            output_f.save()

def submit_code(request):
    print('cocoococoococo')
    username = request.user.username
    language = 'C' #request.POST.get('language','')
    code = request.POST.get('code','')
    c = {}
    submission = Submissions_all(username=username,language=language,datetime=datetime.now(),isRunning='YES')
    submission.save()
    submission = Submissions_all.objects.filter(username=username).last()
    id = submission.id
    submission = Submissions_all.objects.get(pk=int(id))

    fs = FileSystemStorage()
    filename = BASE_DIR + "/compilerApiApp/all_submissions/"
    dirname = filename + str(id)

    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.makedirs(dirname)

    counter = 1
    inputfilecount = 3#request.POST.get['inputfilecount']

    codefile = dirname + "/codefile.cpp"
    codefile_handler=open(codefile,'w+')
    codefile_handler.write(code)
    codefile_handler.close()

    code_file_object = Submissions_all_files(type='codefile',submission=submission,filepath=codefile,errortype='-',runtime='-',memoryused='-')
    code_file_object.save()

    thread_arr = []

    while counter <= inputfilecount :
        thread_arr.append(str(counter))
        thread_arr[counter-1] = threading.Thread(target=run_input_files,args=(request,counter,dirname,c,fs,filename,submission,))
        thread_arr[counter-1].start()
        #run_input_files(request,counter,dirname,c,fs,filename,submission)
        counter = counter + 1

    counter1=1
    while counter1 <= inputfilecount:
        thread_arr[counter1-1].join()
        counter1 = counter1 + 1

    submission.isRunning = 'NO'
    submission.save()
    return render(request,'assignment/showAssignment',c)
