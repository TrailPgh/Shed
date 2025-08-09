from django.shortcuts import render


def index(request):
    return render(request, "shed/index.html")
