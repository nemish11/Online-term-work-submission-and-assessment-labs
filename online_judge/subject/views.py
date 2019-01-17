from django.shortcuts import render

# Create your views here.
def home(request):
    print('helelo')
    return render(request,'subject/index.html')
