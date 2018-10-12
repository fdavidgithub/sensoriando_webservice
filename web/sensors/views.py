from django.shortcuts import render, HttpResponse
from base.models import Category

# Create your views here.
def sensors(request):
    sensors = Sensor.objects.all()
    contexts = []

    for sensor in sensors:
        categ = Category.objects.filter(id = sensor.category_id) 
        local = Local.objects.filter(id = sensor.local_id)
        flags = Flag.opbjects.filter(id = sensor.id)

        sensor_name  = sensor.name 
        sensor_categ = categ[0].name
        sensor_local = local[0].name

        sensor_flags = [str(flag.name) for flag in flags]

        contexts.append({
            'sensor': sensor_name,
            'categ': sensor_categ,
            'local': sensor_local,
            'flags': sensor_flags,
            })

    return render(request, "sensors.html", {'contexts': contexts})

