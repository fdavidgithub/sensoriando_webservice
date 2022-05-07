from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests

def Filters():
    api_url = "http://localhost:8000"
    sensors = requests.get(api_url + "/apisensor/").json()
    tags = requests.get(api_url + "/apitag/").json()
 
    filters = {
        'sensors': sensors,
        'tags': tags,

    }

    return filters

def Home(request):
       
    contexts = {
        'filters': Filters(),

    }
           
    return render(request, 'home.html', {'contexts': contexts})



