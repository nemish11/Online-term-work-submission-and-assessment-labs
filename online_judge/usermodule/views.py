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
                return render(request,'usermodule/index.html')
            return HttpResponseRedirect('/subject/')
        else:
            messages.add_message(request, messages.WARNING, 'Incorect Username or Password')
            return HttpResponseRedirect('/usermodule/login')
    except:
        return render(request,'usermodule/login.html')

def logout(request):
	if request.user.is_authenticated:
		auth.logout(request)
	messages.add_message(request, messages.INFO, 'You are Successfully Logged Out')
	messages.add_message(request, messages.INFO, 'Thanks for visiting.')
	return HttpResponseRedirect('/usermodule/login/')

def add_faculty(request):
    return render(request,'usermodule/add_faculty.html')

def add_student(request):
    return render(request,'usermodule/add_student.html')

def addfaculty(request):
    c = {}
    try:
        if not request.user.is_superuser:
            return HttpResponseRedirect('/admin/')
        else:
            csv_file = request.FILES["facultyfile"]
            if not csv_file.name.endswith('.csv'):
                c['message'] = "please upload .csv file"
                return render(request, 'usermodule/add_faculty.html', c)

            if csv_file.multiple_chunks():
                c['message'] = "File is Too large!"
                return render(request, 'usermodule/add_faculty.html', c)

            data = pd.read_csv(csv_file, names=['username', 'password'])
            x, y = data.shape

            if y != int(2):
                c['message'] = "File Format is not correct"
                return render(request, 'usermodule/add_faculty.html', c)

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

            c['message'] = "User Added Successfully"
            return render(request, 'usermodule/add_faculty.html', c)
    except:
        c['message'] = "Exception Occured"
        return render(request, 'usermodule/add_faculty.html', c)


def addstudent(request):
    c = {}
    if not request.user.is_superuser:
        return HttpResponseRedirect('/admin/')
    else:
        csv_file = request.FILES["studentfile"]
        if not csv_file.name.endswith('.csv'):
            c['message'] = "please upload .csv file"
            return render(request, 'usermodule/add_student.html', c)

        if csv_file.multiple_chunks():
            c['message'] = "File is Too large!"
            return render(request, 'usermodule/add_student.html', c)

        data = pd.read_csv(csv_file, names=['username', 'password','roll_no','year'])
        x, y = data.shape

        if y != int(4):
            c['message'] = "File Format is not correct"
            return render(request, 'usermodule/add_student.html', c)

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

        c['message'] = "User Added Successfully"
        return render(request, 'usermodule/add_student.html', c)

        c['message'] = "Exception Occured"
        return render(request, 'usermodule/add_student.html', c)
