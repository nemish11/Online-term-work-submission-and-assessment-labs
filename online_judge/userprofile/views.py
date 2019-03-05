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
from assignment.models import *
from userprofile.models import Faculty,Student
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required()
def updateFaculty(request):
    return render(request,'userprofile/update_faculty.html')


@login_required()
def updateStudent(request):
    return render(request,'userprofile/update_student.html')


@login_required()
def update_faculty(request):
    try:
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
        if dob:
            faculty.faculty.dob = dob
        faculty.save()
        faculty.faculty.save()
        return HttpResponseRedirect('/userprofile/')
    except:
        c = {}
        c['message'] = "exception Occured!! please try again..."
        return render(request,'userprofile/update_faculty.html',c)
    #return render(request,'userprofile/faculty_profile.html')


@login_required()
def update_student(request):
    try:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        dob = request.POST.get('dob')

        student = User.objects.get(pk=int(request.user.id))
        student.first_name = first_name
        student.last_name = last_name
        student.student.phone_no = phone_no
        student.email = email
        if dob:
            student.student.dob = dob
        student.save()
        student.student.save()

        return HttpResponseRedirect('/userprofile/')
    except:
        c = {}
        c['message'] = "exception Occured!! please try again..."
        return render(request,'userprofile/update_student.html',c)


@login_required()
def updateAdmin(request):
    return render(request,'userprofile/update_admin.html')


@login_required()
def update_admin(request):
    try:
        first_name = request.POST.get('first_name')
        last_name =  request.POST.get('last_name')
        email = request.POST.get('email')

        admin_user = User.objects.get(pk=int(request.user.id))
        admin_user.first_name = first_name
        admin_user.last_name = last_name
        admin_user.email = email
        admin_user.save()
        return HttpResponseRedirect('/userprofile/')
    except:
        c = {}
        c['message'] = "exception Occured!! please try again..."
        return render(request,'userprofile/update_admin.html',c)


@login_required()
def profile(request):
    try:
        c = {}
        all_submissions = Submission.objects.filter(user = request.user)
        accepted_submissions = all_submissions.filter(verdict = "accepted")
        wrong_submissions = all_submissions.filter(verdict = "wrong")

        c['accepted'] = len(accepted_submissions)
        c['wrong'] = len(wrong_submissions)
        c['partially_accepted'] = len(all_submissions) - len(accepted_submissions) - len(wrong_submissions)
        c['total_submissions'] = len(all_submissions)

        if request.user.is_superuser:
            return render(request,'userprofile/admin_profile.html',c)
        if request.user.groups.all()[0].name == 'student':
            return render(request,'userprofile/student_profile.html',c)
        elif request.user.groups.all()[0].name == 'faculty':
            return render(request,'userprofile/faculty_profile.html',c)
        else:
            return render(request,'userprofile/admin_profile.html',c)
    except:
        c = {}
        c['message'] = "exception Occured!! please try again..."
        return render(request,'userprofile/base.html',c)


@login_required()
def allsubmissions(request):
    try:
        c = {}
        submissions = Submission.objects.filter(user = request.user)
        c['submissions'] = submissions
        return render(request,'userprofile/all_submissions.html',c)
    except:
        c = {}
        c['message'] = "exception Occured!! please try again..."
        return render(request,'userprofile/all_submissions.html',c)


@login_required()
def shownotifications(request):
    try:
        user = request.user
        submissions = Submission.objects.filter(user = user, commentunread = True)
        c = {}
        c['submissions'] = submissions
        return render(request,'userprofile/notifications.html',c)
    except:
        return HttpResponseRedirect('/userprofile/')


@login_required()
def change_password_done(request):
    try:
        if request.user.is_authenticated or request.session['usertype'] == "faculty" or request.user.is_superuser:
            username = request.POST.get('username')
            new_password = request.POST.get('new_password')
            #u = User.objects.get(username=str(username))
            u = request.user
            u.set_password(new_password)
            u.save()
            messages.add_message(request, messages.WARNING, 'Password changed successfully!!')
            return HttpResponseRedirect('/subject/')
        else:
            messages.add_message(request, messages.WARNING, 'you are not authorized!!')
            return HttpResponseRedirect('/subject/')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/usermodule/')


@login_required()
def change_password(request):
    try:
        #
        #user = User.objects.get(username=username)
        c = {}
        #c['user'] = user
        return render(request,'userprofile/change_password.html', c);
    except:
        c = {}
        c['message'] = "You can't change the password..."
        return HttpResponseRedirect('/userprofile/')


@login_required()
def change_password_by_faculty(request):
    try:
        c={}
        return render(request,'userprofile/change_password_by_faculty.html',c)
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/usermodule/')


@login_required()
def change_passwordbyfaculty(request):
    if request.session['usertype'] == "faculty" or request.user.is_superuser:
        uname = request.POST.get('uname')
        new_password = request.POST.get('new_password')
        print(uname,new_password)
        u = User.objects.filter(username=uname).update(password=new_password)
        print(u)
        #u.set_password(new_password)
        #u.save()
        c={}
        c['message'] = 'Password changed successfully'
        return HttpResponseRedirect('/userprofile/change_password_by_faculty')
    else:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/usermodule/')

