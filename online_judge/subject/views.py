
from django.shortcuts import render
from django.shortcuts import render,render_to_response
from django.template.context_processors import csrf
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from userprofile.models import Faculty, Student

@login_required()
def all_subject(request):
    if request.user.is_superuser:
        rmlist = []
        subject_list = []
        subject = Subject.objects.all()
        for s in subject:
            if s.status == 1:
                subject_list.append(s)
            else:
                rmlist.append(s)
        return render(request, 'subject/all_subject.html', {'subject_list': subject_list, 'remove_list': rmlist})
    elif request.user.groups.all()[0].name == 'faculty':
        subject_list = Subject.objects.filter(status=True)
        return render(request, 'subject/all_subject.html', {'subject_list': subject_list, 'role': "faculty"})
    elif request.user.groups.all()[0].name == 'student':
        s = Student.objects.get(user=request.user)
        subject_list = Request.objects.filter(student=s, status="approved")
        return render(request, 'subject/all_subject.html', {'subject_list': subject_list, 'role': "student"})
    else:
        return HttpResponseRedirect('/usermodule/')

@login_required()
def add_subject(request):
    if request.user.is_superuser:
        return render(request, 'subject/add_subject.html')
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def addsubject(request):
    if request.user.is_superuser:
        name = request.POST.get("name")
        subject_code = request.POST.get("subject_code")
        s = Subject(name=name, subject_code=subject_code,status=True)
        s.save()
        return HttpResponseRedirect('/subject/all_subject')
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')
@login_required()
def remove_subject(request):
    if request.user.is_superuser:
        return render(request, 'subject/remove_subject.html')
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def removesubject(request):
    if request.user.is_superuser:
        name = request.POST.get('id')
        #subject_code = request.POST.get("subject_code")
        Subject.objects.filter(id=name).update(status=False)
        return HttpResponseRedirect('/subject/all_subject')
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def request_subject(request):
    #print(request.user.groups.all())
    if request.user.is_superuser:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

    if request.user.groups.all()[0].name == 'student':
        subjects=Subject.objects.filter(status=True)
        #print(subjects)
        faculty=Faculty.objects.filter(is_active=True)
        #print(faculty)
        student=Student.objects.get(user=request.user)
        try:
            r_subject=Request.objects.filter(student=student)
        except:
            r_subject=None

        pending_list=[]
        approved_list=[]
        decline_list=[]
        block_list=[]

        for r in r_subject:
            if r.status=="pending":pending_list.append(r)
            elif r.status=="approved":approved_list.append(r)
            elif r.status=="decline":decline_list.append(r)
            else:block_list.append(r)


        sub_list = []
        if r_subject is None:
            sub_list=subjects
        else:
            for s in subjects:
                if s not in approved_list:sub_list.append(s)
        #print(len(sub_list))
        return render(request,'subject/request_subject.html',{'req_subject': sub_list,'faculty_list':faculty,'role':"student",'pending_list':pending_list,'approved_list':approved_list,'decline_list':decline_list,'block_list':block_list})
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def pending_request(request):
    f = request.POST.get('faculty')
    s = request.POST.get('subject')
    if s is None or f is None:
        messages.add_message(request, messages.WARNING, "Please select both faculty as well as subject")
        return HttpResponseRedirect('/subject/request_subject')
    fobj = Faculty.objects.get(id=f)
    sobj = Subject.objects.get(id=s)
    stuobj = Student.objects.get(user=request.user)
    try:
        checkobj=Request.objects.get(faculty=fobj,student=stuobj,subject=sobj)
    except:
        checkobj=None
    if checkobj is not None:
        if checkobj.status == "pending" or checkobj.status=="approved":
            messages.add_message(request, messages.WARNING, "Subject is already requested or approved !!")
            return HttpResponseRedirect('/subject/request_subject')
        elif checkobj.status == "decline":
            Request.objects.get(faculty=fobj, student=stuobj, subject=sobj).update(status="pending")
            messages.add_message(request, messages.WARNING, "Subject is again requested!!")
            return HttpResponseRedirect('/subject/request_subject')
        else:
            messages.add_message(request, messages.WARNING, "You can't request this subject!!")
            return HttpResponseRedirect('/subject/request_subject')
    r = Request(faculty=fobj, student=stuobj, subject=sobj, status="pending")
    r.save()
    messages.add_message(request, messages.INFO, "Subject is requested to faculty "+str(fobj.user))
    return HttpResponseRedirect('/subject/request_subject')

@login_required()
def request_list(request):
    if request.user.is_superuser:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

    if request.user.groups.all()[0].name == 'faculty':
        faculty=Faculty.objects.get(user=request.user)
        req_list=Request.objects.filter(faculty=faculty,status="pending")
        return render(request,'subject/request_list.html',{'req_list':req_list,'role':"faculty"})
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def approved_request(request):
    stu=request.POST.get('id')
    s=request.POST['status']
    #print(s)
    Request.objects.filter(id=stu).update(status=s)
    messages.add_message(request, messages.INFO, "Request is "+s)
    return HttpResponseRedirect('/subject/request_list')
