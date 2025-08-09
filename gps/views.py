from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'gps/index.html')

def upload_image(request):
    # return HttpResponse("Upload Image")
    return render(request, 'gps/upload_image.html')
