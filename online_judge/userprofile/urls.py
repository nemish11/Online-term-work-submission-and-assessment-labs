from django.conf.urls import url
from django.urls import path
from .views import updateStudent,updateFaculty,update_student,update_faculty,profile,update_admin,updateAdmin,allsubmissions

urlpatterns = [
    url(r'updateStudent',updateStudent),
    url(r'allsubmissions',allsubmissions),
    url(r'updateFaculty',updateFaculty),
    url(r'updateAdmin',updateAdmin),
    url(r'update_student',update_student),
    url(r'update_faculty',update_faculty),
    url(r'update_admin',update_admin),
    url(r'profile',profile),
    url(r'',profile)
]
