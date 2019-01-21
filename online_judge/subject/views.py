from django.shortcuts import render
from django.shortcuts import render,render_to_response
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from userprofile.models import Faculty, Student

@login_required()
def all_subject(request):
    try:
        if request.user.is_superuser :
            rmlist=[]
            subject_list=[]
            subject=Subject.objects.all()
            for s in subject:
                if s.status==1:subject_list.append(s)
                else:rmlist.append(s)
            return render(request,'subject/all_subject.html', {'subject_list': subject_list,'remove_list':rmlist})
        elif hasGroup(request.user, 'faculty') :
            subject_list=Subject.objects.get(status=True)
            return render(request, 'subject/all_subject.html', {'subject_list': subject_list})
        else:
            subject_list=Request.objects.get(student=request.user,status="approved")
            return render(request,'subject/all_subject.html', {'subject_list': subject_list})

    except:
        return render(request,'subject/all_subject.html', {'subject_list': None})

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
        name = request.POST.get("name")
        subject_code = request.POST.get("subject_code")
        Subject.objects.filter(name=name, subject_code=subject_code).update(status=False)
        return render(request, 'subject/all_subject.html')
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def request_subject(request):
    if request.user.has_Group('student'):
        subjects=Subject.objects.get(status=True)
        faculty=Faculty.objects.all()
        r_subject=Request.objects.get(status="approved")
        sub_list=[]
        for s in subjects:
            if s not in r_subject:sub_list.append(s)
        return render(request,'subject/request_subject.html',{'req_subject': sub_list,'faculty':faculty})
    else:
        messages.add_message(request, messages.WARNING, 'You are not authorized!!')
        return HttpResponseRedirect('/subject/all_subject')
@login_required()
def pending_request(request):
    f=request.POST.get('faculty')
    s=request.POST.get('subject')
    fobj=Faculty.objects.get(id=f)
    sobj=Subject.objects.get(id=s)
    stuobj=Student.objects.get(user=request.user)
    r=Request(request_faculty=fobj,request_student=stuobj,request_subject=sobj,status=pending)
    r.save()
    messages.add_message(request,  "Subject is requested to faculty "+fobj.user.name)
    return HttpResponseRedirect('/subject/request_subject')

@login_required()
def request_list(request):
    if request.user.has_Group('faculty'):
        req_list=Request.objects.get(status="pending")
        return render(request,'subject/request_list.html',{'req_list':req_list})


@login_required()
def approved_request(request):
    stu=request.POST.get('id')
    r=Request.objects.get(id=stu)
    r.status=request.POST['status']
    r.save()
    return HttpResponseRedirect('/subject/request_list')




