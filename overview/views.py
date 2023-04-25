from django.shortcuts import render, redirect
from django.http import HttpResponse
from base.views import callAPI

import pycountry

def Filters():
    sensors = callAPI("/sensor/")
    sensortags = callAPI("/sensor/tag/")
 
    filters = {
        'sensors': sensors,
        'tags': sensortags,

    }

    return filters

def Home(request):
    jsonResult = callAPI("/data/public/thing")

    for item in jsonResult:
        if "country" in item["account"]:
            country_code = item["account"]["country"]
            country_name = pycountry.countries.get(alpha_2=country_code).name
            item["account"]["country"] = country_name

    contexts = {
        'filters': Filters(),
        'things': jsonResult,

    }
           
    return render(request, 'home.html', {'contexts': contexts})



