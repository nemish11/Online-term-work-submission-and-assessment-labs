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

def updateFaculty(request):
    return render(request,'userprofile/update_faculty.html')

def updateStudent(request):
    return render(request,'userprofile/update_student.html')

def update_faculty(request):
    first_name = request.POST.get('first_name')
    last_name =  request.POST.get('last_name')
    phone_no = request.POST.get('phone_no')
    email = request.POST.get('email')
    dob = request.POST.get('dob')

    faculty = User.objects.get(pk=int(request.user.id))
    faculty.first_name = first_name
    faculty.last_name = last_name
    faculty.faculty.phone_no = phone_no
    faculty.email = email
    faculty.student.dob = dob
    faculty.save()
    faculty.faculty.save()

    return render(request,'userprofile/faculty_profile.html')

def update_student(request):
    first_name = request.POST.get('first_name')
    last_name =  request.POST.get('last_name')
    phone_no = request.POST.get('phone_no')
    email = request.POST.get('email')
    dob = request.POST.get('dob')

    student = User.objects.get(pk=int(request.user.id))
    student.first_name = first_name
    student.last_name = last_name
    student.student.phone_no = phone_no
    student.email = email
    student.student.dob = dob
    student.save()
    student.student.save()

    return render(request,'userprofile/student_profile.html')

def updateAdmin(request):
    return render(request,'userprofile/update_admin.html')

def update_admin(request):
    first_name = request.POST.get('first_name')
    last_name =  request.POST.get('last_name')
    email = request.POST.get('email')
    
    admin_user = User.objects.get(pk=int(request.user.id))
    admin_user.first_name = first_name
    admin_user.last_name = last_name
    admin_user.email = email
    admin_user.save()
    return render(request,'userprofile/admin_profile.html')

def profile(request):
    c = {}
    if request.user.is_superuser:
        return render(request,'userprofile/admin_profile.html',c)
    if request.user.groups.all()[0].name == 'student':
        return render(request,'userprofile/student_profile.html',c)
    elif request.user.groups.all()[0].name == 'faculty':
        return render(request,'userprofile/faculty_profile.html',c)
    else:
        return render(request,'userprofile/admin_profile.html',c)

def allsubmissions(request):
    c = {}
    return render(request,'userprofile/all_submissions.html',c)
