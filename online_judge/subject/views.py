from django.shortcuts import render

# Create your views here.
def home(request):
    print('heyyyyy')
    return render(request,'subject/index.html')
