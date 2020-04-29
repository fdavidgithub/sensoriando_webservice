from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

import unicodecsv

from .models import Things, Thingsdata, Thingsflags, Sensors, Accounts, Accountsthings

# Create your views here.
@csrf_exempt
def topics(request):
    # Monta resposta em CSV
    response = HttpResponse(content_type='text/csv')
    writer = unicodecsv.writer(response, encoding='UTF-8')

    valid = Accounts.objects.filter(username=request.POST.get("username"), 
                                   password=request.POST.get("password"),
                                  )
    
    regs = Sensors.objects.filter(user_ptr_id=valid[0].user_ptr_id)

    for r in regs:
        name="{}/{}".format(r.id_local, r.name)
        row = [r.id, name, r.token]

        writer.writerow(row)

    return response

@csrf_exempt
def export_csv(request):
    # Monta resposta em CSV
    response = HttpResponse(content_type='text/csv')
    writer = unicodecsv.writer(response, encoding='UTF-8')

    valid = Accounts.objects.filter(username=request.POST.get("username"), 
                                   password=request.POST.get("password"),
                                  )
    
    regs = Sensors.objects.filter(user_ptr_id=valid[0].user_ptr_id)

    for r in regs:
        name="{}/{}".format(r.id_local, r.name)
        row = [r.id, name, r.token]

        writer.writerow(row)

    return response

def ListPublicSensors(request):
    accounts = Accounts.objects.filter(ispublic = True)
    contexts = []

    for account in accounts:
        things = Things.objects.filter(accountsthings__id_account = account.id)
       
        for thing in things:
            try:
                thingdatum = Thingsdata.objects.filter(id_thing = thing.id).latest('id')
                last_update = thingdatum.dt
            except:
                last_update = 'nenhuma'

            sensors = Sensors.objects.filter(thingsdata__id_thing = thing.id).distinct()

            contexts.append({
                'name': thing.name,
                'city': account.city,
                'state': account.state,
                'country': account.country,
                'last_update': last_update,
                'flags': Thingsflags.objects.filter(id_thing = thing.id),
                'sensors': sensors,
            })

    return render(request, 'home.html', {'contexts': contexts})

def SearchPublicSensors(request):
    accounts = Accounts.objects.filter(ispublic = True)
    contexts = []

    return render(request, 'search.html', {'contexts': contexts})

def RedirectSensoriando(request):
    return redirect('http://www.sensoriando.com.br')

def SensorDetails(request):
    contexts = []

    return render(request, 'sensor.html', {'contexts': contexts})


