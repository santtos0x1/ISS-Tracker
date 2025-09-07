from django.shortcuts import render

def home(request):
    return render(request, "iss/home.html")

def iss_positition(request):
    ...