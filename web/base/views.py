from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Count,Avg,Value,CharField
from django.db.models.functions import Extract, Concat 

import unicodecsv

from .models import Things, Thingsdata, Thingsflags, Sensors, Accounts, Accountsthings, Vwthingsdata, Sensorsunits

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
                'id': thing.id,
                'name': thing.name,
                'city': account.city,
                'state': account.state,
                'country': account.country,
                'last_update': last_update,
                'flags': Thingsflags.objects.filter(id_thing = thing.id),
                'sensors': sensors,
            })

    return render(request, 'home.html', {'contexts': contexts})

def MapSensors(request):
    accounts = Accounts.objects.values('country').order_by('country').annotate(total=Count('country'))
    contexts = {
        'countries': accounts, 
    }

    return render(request, 'map.html', {'contexts': contexts})

def RedirectSensoriando(request):
    return redirect('http://www.sensoriando.com.br')

def SensorDetails(request, id_thing):
    chartview = request.COOKIES.get('chartview')
    if chartview is None:
        chartview = 's' #default: seconds

    thing = Things.objects.filter(id = id_thing)
    account = Accounts.objects.filter(accountsthings__id_thing = id_thing)
    sensors = Sensors.objects.filter(thingsdata__id_thing = id_thing).distinct()
    units = Sensorsunits.objects.filter(id_sensor__thingsdata__id_thing = id_thing, isdefault=True).distinct()
    data = Vwthingsdata.objects.filter(id_thing = id_thing)
  
    if account[0].ispublic:
        access = 'Publico'
    else:
        access = 'Privado'

    if chartview == 's':
        chartview_label = data.last().payload_dt.strftime("%d/%m/%Y %H:%M")
        chartview_title = 'Segundos'

        data = data.annotate(group_dt=Concat(Extract('payload_dt', 'second'), Value('s'), output_field=CharField()))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor') 
    elif chartview == 'm':
        chartview_label = data.last().payload_dt.strftime("%d/%m/%Y")
        chartview_title = 'Minutos'

        data = data.annotate(group_dt=Concat(Extract('payload_dt', 'hour'), Value(':'), Extract('payload_dt', 'minute'), output_field=CharField()))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor') 
    elif chartview == 'h':
        chartview_label = data.last().payload_dt.strftime("%d/%m/%Y")
        chartview_title = 'Horas'

        data = data.annotate(group_dt=Concat(Extract('payload_dt', 'hour'), Value('h'), output_field=CharField()))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor') 
    elif chartview == 'd':
        chartview_label = data.last().payload_dt.strftime("%m/%Y")
        chartview_title = 'Dias'

        data = data.annotate(group_dt=Extract('payload_dt', 'day'))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor')
    elif chartview == 'M':
        chartview_label = data.last().payload_dt.strftime("%Y")
        chartview_title = 'Meses'

        data = data.annotate(group_dt=Extract('payload_dt', 'month'))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor')
    elif chartview == 'y':
        chartview_label = ''
        chartview_title = 'Anos'
 
        data = data.annotate(group_dt=Extract('payload_dt', 'year'))
        data = data.values('group_dt', 'id_sensor')
        data = data.annotate(group_value=Avg('payload_value'))
        data = data.order_by('group_dt', 'id_sensor')
    else:
        chartview_label = 'ops!!'

    print(data)

    context = {
        'thing': thing[0].name,
        'canva': 'chart-line',
        'chart_file': 'chart-line.js',
        'city': account[0].city,
        'state': account[0].state,
        'label': chartview_label,
        'title': chartview_title,
        'country': account[0].country,
        'access': access,
        'sensors': sensors,
        'units': units,
        'flags': Thingsflags.objects.filter(id_thing = id_thing),
        'data': data,
    }

    return render(request, 'sensor.html', {'context': context})


