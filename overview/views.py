from django.shortcuts import render, redirect
from django.http import HttpResponse

from base.views import callAPI
from users.views import check_and_refresh_token
from base.models import ThingsSensorsDataModel

import pycountry
import json

def Filters():
    sensors = callAPI("/sensors/")
    sensortags = callAPI("/sensors/tags/")
 
    filters = {
        'sensors': sensors,
        'tags': sensortags,

    }

    return filters

def readCookie(request):
    cookieValue = request.COOKIES.get("setFilterHome")

    if cookieValue:
        jsonCookie = json.loads(cookieValue)

        if "country" in jsonCookie:
            country = pycountry.countries.get(name=jsonCookie["country"])
            jsonCookie["country"] = country.alpha_2 
    else:
        jsonCookie = None

    return jsonCookie

def getCountry(jsonResult):
    if jsonResult:
        for item in jsonResult:
            if "country" in item["account"]:
                country_code = item["account"]["country"]
                country_name = pycountry.countries.get(alpha_2=country_code).name
                item["account"]["country"] = country_name

    return jsonResult

def Public(request):
    jsonParams = readCookie(request)
    jsonResult = callAPI(endpoint = "/things/", data = jsonParams, method = "POST")
    
    jsonResult = getCountry(jsonResult)

    contexts = {
        'filters': Filters(),
        'things': jsonResult,
        'filterApply': jsonParams,

    }
    
    return render(request, 'index.html', {'contexts': contexts})

def getStatistics():
    try:
        token = check_and_refresh_token()
    except:
        token = None

    jsonResult = callAPI(endpoint = "/data/stats/private/", token = token)
    return jsonResult

def Private(request):
    try:
        token = check_and_refresh_token()
    except:
        token = None

    jsonParams = readCookie(request)
    jsonResult = callAPI(endpoint = "/things/private/" , data = jsonParams, \
                         method = "POST", token = token)
    
    jsonResult = getCountry(jsonResult)
   
    contexts = {
        'filters': Filters(),
        'things': jsonResult,
        'filterApply': jsonParams,
        'stats': getStatistics(),
    }
    
    return render(request, 'home.html', {'contexts': contexts})



