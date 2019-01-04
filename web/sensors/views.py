from django.shortcuts import render, HttpResponse
from base.models import Category
from . models import Sensor, Local, Flag
from accounts.models import Account

# Create your views here.
def sensors(request):
    sensors = Sensor.objects.filter(local__account__is_public = True)
    contexts = []

    for sensor in sensors:
        categ = Category.objects.filter(pk = sensor.category_id) 
        
        local = Local.objects.filter(pk = sensor.local_id)
        local_id = local.values('account')
        tmp = local_id[0]
        id = tmp['account']

        account = Account.objects.filter(pk = id)

        contexts.append({
            'sensor': sensor.name,
            'city': account[0].city,
            'uf': account[0].uf,
            'id': account[0].id,
            'categ': categ[0].name,
            'local': local[0].name,
            'flags': Flag.objects.filter(sensor = sensor.id),
        })
 
    return render(request, "sensors.html", {'contexts': contexts})

