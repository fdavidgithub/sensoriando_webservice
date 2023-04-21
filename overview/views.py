from django.shortcuts import render, redirect
from django.http import HttpResponse
from base.views import callAPI

def Filters():
    sensors = callAPI("/sensor/")
    sensortags = callAPI("/sensor/tag/")
 
    filters = {
        'sensors': sensors,
        'tags': sensortags,

    }

    return filters

def Home(request):
    contexts = {
        'filters': Filters(),
        'things': callAPI("/data/public/thing"),

    }
           
    return render(request, 'home.html', {'contexts': contexts})



