from django.shortcuts import render
from django.shortcuts import render,render_to_response
from django.template.context_processors import csrf
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from userprofile.models import Faculty, Student
from django.db.models import Max,Min


@login_required()
def all_subject(request):
    try:
        ymax = Student.objects.all().aggregate(Max('year'))['year__max']
        ymin = Student.objects.all().aggregate(Min('year'))['year__min']
        if ymax is None:
            ymax = 2016
            ymin = 2016
        c={}
        c['min_year'] = ymin
        c['max_year'] = ymax
        if request.user.is_superuser:
            rmlist = []
            subject_list = []
            subject = Subject.objects.all()
            for s in subject:
                if s.status == 1:
                    subject_list.append(s)
                else:
                    rmlist.append(s)
            c['subject_list'] = subject_list
            c['removed_subject_list'] = rmlist
            return render(request, 'subject/all_subject.html', c)
        elif request.user.groups.all()[0].name == 'faculty':
            f=Faculty.objects.get(user=request.user)
            student_list=Request.objects.filter(faculty=f,status="approved")
            subject_list = Subject.objects.filter(status=True)
            c['subject_list'] = subject_list
            c['role'] = "faculty"
            c['stu_list'] = student_list
            return render(request, 'subject/all_subject.html', c)
        elif request.user.groups.all()[0].name == 'student':
            s = Student.objects.get(user=request.user)
            subject_list = Request.objects.filter(student=s, status="approved")
            c['subject_list'] = subject_list
            c['role'] = "student"
            return render(request, 'subject/all_subject.html', c)
        else:
            return HttpResponseRedirect('/usermodule/')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/usermodule/')


@login_required()
def add_subject(request):
    try:
        if request.user.is_superuser:
            return render(request, 'subject/all_subject.html')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def addsubject(request):
    try:
        if request.user.is_superuser:
            name = request.POST.get("name")
            subject_code = request.POST.get("subject_code")
            s = Subject(name=name, subject_code=subject_code,status=True)
            s.save()
            return HttpResponseRedirect('/subject/all_subject')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def readd_subject(request):
    try:
        if request.user.is_superuser:
            subjectid = request.POST.get('subjectid')
            Subject.objects.filter(id=subjectid).update(status=True)
            return HttpResponseRedirect('/subject/all_subject')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def removesubject(request):
    try:
        if request.user.is_superuser:
            name = request.POST.get('subjectid')
            Subject.objects.filter(id=name).update(status=False)
            return HttpResponseRedirect('/subject/all_subject')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def request_subject(request):
    try:
        if request.user.is_superuser:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')

        if request.user.groups.all()[0].name == 'student':
            subjects = Subject.objects.filter(status=True)
            faculty = Faculty.objects.filter(is_active=True)
            student = Student.objects.get(user=request.user)
            try:
                r_subject = Request.objects.filter(student=student)
            except:
                r_subject = None

            slist = []

            dic = {}
            dic2 = {}
            for s in subjects:
                dic[s.name] = 1
                dic2[s.name] = s

            pending_list = []
            approved_list = []
            decline_list = []
            block_list = []

            for r in r_subject:
                if r.status == "pending":
                    pending_list.append(r)
                    dic[r.subject.name] = 0
                elif r.status == "approved":
                    approved_list.append(r)
                    dic[r.subject.name] = 0
                elif r.status == "decline":
                    decline_list.append(r)
                    dic[r.subject.name] = 1
                else:
                    block_list.append(r)
                    dic[r.subject.name] = 0
            for key in dic:
                if dic[key] == 1:
                    slist.append(dic2[key])
            c = {}
            c['req_subject'] = slist
            c['faculty_list'] = faculty
            c['role'] = "student"
            c['pending_list'] = pending_list
            c['approved_list'] = approved_list
            c['decline_list'] = decline_list
            c['block_list'] = block_list
            return render(request,'subject/request_subject.html',c)
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


'''@login_required()
def selectedsubject(request): #not required
    try:
        subjectid = request.POST.get('subjectid')
        subjectyear = request.POST.get('subjectyear')
        request.session['subjectyear'] = subjectyear
        request.session['subjectid'] = subjectid
        return HttpResponseRedirect('/assignment/showWeek')
    except:
        return HttpResponseRedirect('/subject/')
'''


@login_required()
def pending_request(request):
    try:
        if request.session['usertype'] == "student":
            f = request.POST.get('faculty')
            s = request.POST.get('subject')
            if s is None or f is None:
                messages.add_message(request, messages.WARNING, "Please select both faculty as well as subject")
                return HttpResponseRedirect('/subject/request_subject')
            fobj = Faculty.objects.get(id=f)
            sobj = Subject.objects.get(id=s)
            stuobj = Student.objects.get(user=request.user)
            try:
                checkobj = Request.objects.filter(faculty=fobj,student=stuobj,subject=sobj)[0]
            except:
                checkobj = None
            if checkobj is not None:
                if checkobj.status == "pending" or checkobj.status=="approved":
                    messages.add_message(request, messages.WARNING, "Subject is already requested or approved !!")
                    return HttpResponseRedirect('/subject/request_subject')
                elif checkobj.status == "decline":
                    Request.objects.filter(faculty=fobj, student=stuobj, subject=sobj).update(status="pending")
                    messages.add_message(request, messages.WARNING, "Subject is again requested!!")
                    return HttpResponseRedirect('/subject/request_subject')
                else:
                    messages.add_message(request, messages.WARNING, "You can't request this subject!!")
                    return HttpResponseRedirect('/subject/request_subject')
            r = Request(faculty=fobj, student=stuobj, subject=sobj, status="pending")
            r.save()
            messages.add_message(request, messages.INFO, "Subject is requested to faculty "+str(fobj.user))
            return HttpResponseRedirect('/subject/request_subject')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')

@login_required()
def removerequest(request):
    try:
        if request.user.groups.all()[0].name == 'student':
            requestid = request.POST.get('requestid')
            Request.objects.filter(id=requestid).update(status="decline")
            return HttpResponseRedirect('/subject/request_subject')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def request_list(request):
    try:
        if request.user.is_superuser:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')

        if request.user.groups.all()[0].name == 'faculty':
            faculty = Faculty.objects.get(user=request.user)
            try:
                request_list = Request.objects.filter(faculty=faculty, status="pending")
            except:
                request_list = None

            subjects = Subject.objects.filter(status=True)

            ymax = Student.objects.all().aggregate(Max('year'))['year__max']
            ymin = Student.objects.all().aggregate(Min('year'))['year__min']

            c = {}
            c['request_list'] = request_list
            c['role'] = "faculty"
            c['min_year'] = ymin
            c['max_year'] = ymax
            c['subjects'] = subjects
            return render(request, 'subject/request_list.html', c)
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/all_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


'''@login_required()
def set_subject_for_studentlist(request):
    try:
        if request.session['usertype'] == 'faculty' :
            subjectid = request.POST.get('subjectid')
            year = request.POST.get('year')
            request.session['studentlist_subjectid'] = subjectid
            request.session['studentlist_year'] = year
            return HttpResponseRedirect('/subject/student_list')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_subject')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')
'''

@login_required()
def student_list(request):
    try:
        if request.user.groups.all()[0].name == 'faculty':
            faculty = Faculty.objects.get(user=request.user)
            subjectid = request.GET.get('subjectid')
            year1 = request.GET.get('year')
            subjectid = int(subjectid)
            year1 = int(year1)
            subject = Subject.objects.get(id=int(subjectid))
            students = Request.objects.filter(faculty=faculty,  subject=subject, status="approved")
            student_list = []
            for s in students:
                if int(s.student.year) == int(year1):
                    student_list.append(s)
            c = {}
            c['subject'] = subject
            c['faculty'] = faculty
            c['students'] = student_list
            return render(request, 'subject/student_list.html', c)
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_list')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def approved_request(request):
    try:
        if request.user.groups.all()[0].name == 'faculty':
            id = request.POST.get('id')
            s = request.POST.get('status')
            Request.objects.filter(id=id).update(status=s)
            messages.add_message(request, messages.INFO, "Request is "+s)
            return HttpResponseRedirect('/subject/request_list')
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_list')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')


@login_required()
def remove_student(request):
    try:
        if request.user.groups.all()[0].name == 'faculty':
            id = int(request.POST.get('requestid'))
            Request.objects.filter(id=id).update(status="decline")
            req = Request.objects.filter(id=id)[0]
            subjectid = req.subject.id
            year = req.student.year
            return HttpResponseRedirect('/subject/student_list/?subjectid='+str(subjectid)+'&year='+str(year))
        else:
            messages.add_message(request, messages.WARNING, 'You are not authorized!!')
            return HttpResponseRedirect('/subject/request_list')
    except:
        messages.add_message(request, messages.WARNING, 'Something wrong!!')
        return HttpResponseRedirect('/subject/all_subject')
