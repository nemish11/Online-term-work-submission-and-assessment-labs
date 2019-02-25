from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from django.contrib import messages
import pandas as pd
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import pandas as pd
from userprofile.models import Student,Faculty
from userprofile.models import Faculty,Student
import datetime


def login(request):
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return render(request,'usermodule/index.html')
            return HttpResponseRedirect('/subject/')
        else:
            c = {}
            c.update(csrf(request))
            return render(request, 'usermodule/login.html', c)
    except:
        return render(request,'usermodule/login.html')


def auth_view(request):
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return render(request,'usermodule/index.html')
            return HttpResponseRedirect('/subject/')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect('/subject/')
            usertype = request.user.groups.all()[0].name
            request.session['usertype'] = usertype
            return HttpResponseRedirect('/subject/')
        else:
            messages.add_message(request, messages.WARNING, 'Incorect Username or Password')
            return HttpResponseRedirect('/usermodule/login')
    except:
        return render(request,'usermodule/login.html')


@login_required()
def logout(request):
    try:
        if request.user.is_authenticated:
            auth.logout(request)
        messages.add_message(request, messages.INFO, 'You are Successfully Logged Out')
        messages.add_message(request, messages.INFO, 'Thanks for visiting.')
        #request.session.clear()
        return HttpResponseRedirect('/usermodule/login/')
    except:
        messages.add_message(request, messages.WARNING, 'Exception Occured..please try again.')
        return render(request,'usermodule/login.html')


@login_required()
def add_faculty(request):
    try:
        c = {}
        c['current_faculty'] = Faculty.objects.filter(is_active= True)
        c['past_faculty'] = Faculty.objects.filter(is_active=False)
        return render(request,'usermodule/add_faculty.html',c)
    except:
        return HttpResponseRedirect('/subject/')


@login_required()
def add_student(request):
    try:
        c = {}
        c['current_student'] = Student.objects.filter(is_active= True)
        c['past_student'] = Student.objects.filter(is_active=False)
        return render(request,'usermodule/add_student.html',c)
    except:
        return HttpResponseRedirect('/subject/')


@login_required()
def addfaculty(request):
    try:
        if not request.user.is_superuser:
            return HttpResponseRedirect('/admin/')
        else:
            csv_file = request.FILES["facultyfile"]
            if not csv_file.name.endswith('.csv'):
                messages.add_message(request, messages.WARNING, 'please upload .csv file!!!')
                return HttpResponseRedirect('/usermodule/add_faculty')

            if csv_file.multiple_chunks():
                messages.add_message(request, messages.WARNING, 'file is too large!!!')
                return HttpResponseRedirect('/usermodule/add_faculty')

            data = pd.read_csv(csv_file, names=['username', 'password'])
            x, y = data.shape

            if y != int(2):
                messages.add_message(request, messages.WARNING, 'File Format is not correct!!!')
                return HttpResponseRedirect('/usermodule/add_faculty')

            for i in range(x):
                username = data['username'][i]
                password = data['password'][i]
                faculty = User.objects.create_user(username=username,password=password)
                faculty.save()
                faculty.faculty = Faculty(is_active = True,dob=datetime.date.today())
                faculty.faculty.save()

                group = Group.objects.get(name='faculty')
                group.user_set.add(faculty)
                group.save()

            messages.add_message(request, messages.INFO, 'User Added sucessfully')
            return HttpResponseRedirect('/usermodule/add_faculty')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_faculty')


@login_required()
def addstudent(request):
    try:
        if not request.user.is_superuser:
            return HttpResponseRedirect('/admin/')
        else:
            csv_file = request.FILES["studentfile"]
            if not csv_file.name.endswith('.csv'):
                messages.add_message(request, messages.WARNING, 'please upload .csv file!!!')
                return HttpResponseRedirect('/usermodule/add_student')

            if csv_file.multiple_chunks():
                messages.add_message(request, messages.WARNING, 'file is too large!!!')
                return HttpResponseRedirect('/usermodule/add_student')

            data = pd.read_csv(csv_file, names=['username', 'password','roll_no','year'])
            x, y = data.shape

            if y != int(4):
                messages.add_message(request, messages.WARNING, 'File Format is not correct!!!')
                return HttpResponseRedirect('/usermodule/add_student')

            for i in range(x):
                username = data['username'][i]
                password = data['password'][i]
                roll_no = data['roll_no'][i]
                year = data['year'][i]
                student = User.objects.create_user(username = username, password = password)
                student.save()
                student.student = Student(roll_no = roll_no, year = int(year),dob = datetime.date.today())
                student.student.save()
                group = Group.objects.get(name='student')
                group.user_set.add(student)
                group.save()

            messages.add_message(request, messages.INFO, 'User Added sucessfully')
            return HttpResponseRedirect('/usermodule/add_student')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please check file data and shape..try again!!!')
        return HttpResponseRedirect('/usermodule/add_student')


@login_required()
def removefaculty(request):
    try:
        facultyid = request.POST.get('facultyid')
        faculty = Faculty.objects.get(pk=int(facultyid))
        faculty.delete()
        messages.add_message(request, messages.INFO, 'Faculty Removed sucessfully')
        return HttpResponseRedirect('/usermodule/add_faculty')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_faculty')


@login_required()
def addtopastfaculty(request):
    try:
        facultyid = request.POST.get('facultyid')
        faculty = Faculty.objects.get(pk=int(facultyid))
        faculty.is_active = False
        faculty.save()
        messages.add_message(request, messages.INFO, 'Faculty Added to past Faculty sucessfully')
        return HttpResponseRedirect('/usermodule/add_faculty')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_faculty')


@login_required()
def addtoactivefaculty(request):
    try:
        facultyid = request.POST.get('facultyid')
        faculty = Faculty.objects.get(pk=int(facultyid))
        faculty.is_active = True
        faculty.save()
        messages.add_message(request, messages.INFO, 'Faculty Added to Active Faculty sucessfully')
        return HttpResponseRedirect('/usermodule/add_faculty')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_faculty')


@login_required()
def removestudent(request):
    try:
        studentid = request.POST.get('studentid')
        student = Student.objects.get(pk=int(studentid))
        student.delete()
        messages.add_message(request, messages.INFO, 'student removed sucessfully')
        return HttpResponseRedirect('/usermodule/add_student')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_student')


@login_required()
def addtopaststudent(request):
    try:
        studentid = request.POST.get('studentid')
        student = Student.objects.get(pk=int(studentid))
        student.is_active = False
        student.save()
        messages.add_message(request, messages.WARNING, 'student added to past student sucessfully')
        return HttpResponseRedirect('/usermodule/add_student')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_student')


@login_required()
def addtoactivestudent(request):
    try:
        studentid = request.POST.get('studentid')
        student = Student.objects.get(pk=int(studentid))
        student.is_active = True
        student.save()
        messages.add_message(request, messages.WARNING, 'student added to active student sucessfully')
        return HttpResponseRedirect('/usermodule/add_student')
    except:
        messages.add_message(request, messages.WARNING, 'Something went wrong...please try again!!!')
        return HttpResponseRedirect('/usermodule/add_student')
