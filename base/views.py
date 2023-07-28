from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Avg, Value, CharField
from django.db.models.functions import Extract, Concat

from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.response import Response

import requests

def callAPI(endpoint, data = None, method = "GET", token = None):
    headers = {}
    if token:
        headers['Authorization'] = 'Bearer ' + token

    try:
        if method.upper() == "POST" or data:
            response = requests.post(settings.PREFIX_API + endpoint, data, headers=headers)
        else:
            response = requests.get(settings.PREFIX_API + endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return Response({'warning': 'Invalid request: ' + str(response.status_code)})
    except:
        return Response({'error': 'Bad request: ' + settings.PREFIX_API + endpoint})
        

def MapSensors(request):
    accounts = Accounts.objects.values('country').order_by('country').annotate(total=Count('country'))
    contexts = {
        'countries': accounts, 
    }

    return render(request, 'map.html', {'contexts': contexts})

def NotFound(request):
    contexts = []
    return render(request, '404.html', {'contexts': contexts})

def RedirectSensoriando(request):
    return redirect('http://www.sensoriando.com.br')


