from django.shortcuts import render, redirect
from django.http import HttpResponse
from base.views import callAPI

import pycountry
import json

def Filters():
    sensors = callAPI("/sensor/")
    sensortags = callAPI("/sensor/tag/")
 
    filters = {
        'sensors': sensors,
        'tags': sensortags,

    }

    return filters

def Home(request):
    cookieValue = request.COOKIES.get("setFilterHome")

    if cookieValue:
        jsonData = json.loads(cookieValue)

        if "country" in jsonData:
            country = pycountry.countries.get(name=jsonData["country"])
            jsonData["country"] = country.alpha_2 
    else:
        jsonData = None

    jsonResult = callAPI("/data/public/thing/", jsonData)

    for item in jsonResult:
        if "country" in item["account"]:
            country_code = item["account"]["country"]
            country_name = pycountry.countries.get(alpha_2=country_code).name
            item["account"]["country"] = country_name

    contexts = {
        'filters': Filters(),
        'things': jsonResult,
        'filterApply': jsonData,

    }
    
    return render(request, 'home.html', {'contexts': contexts})



