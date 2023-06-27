from api.views import *
from django.conf import settings

#from constants import CHART_DEFAULT, CHARTVIEW_DEFAULT, MAX_PRECISION
import unicodecsv, datetime


def ListPublicSensors(filterSensor=None, filterTag=None):
    data = []
    
    publicAccounts = requests.get(settings.PREFIX_API + "/account/public/").json()
    public = requests.get(settings.PREFIX_API + "/account/thing/sensor/tag/").json()
    
    for public in publics:
        filterControl = False

        if filterSensor is not None:
            if filterSensor in public['sensors']:
                filterControl = True

        if filterTag is not None:
            if filterTag in public['tags']:
                filterControl = True

        if filterControl:
            data.append({
                'thing': public["name"],
                'city': public['city'],
                'estate': public['state'],
                'country': public['country'],
                'last_update': "2022-05-07",
                'tags': public["tags"],
                'sensors': public["sensors"],
    
            })

    return data
'''
def SensorDetails(request, slug_thing):
    # Get from cookies
    chartview = request.COOKIES.get('chartview')
   
    # Get data
    thing = Things.objects.get(name = slug_thing.replace("-", " "))
    account = Accounts.objects.get(accountsthings__id_thing = thing.id)
    id_plan = account.id_plan.id

    if Plans.objects.get(id = id_plan).ispublic:
        access = 'Publico'
    else:
        access = 'Privado'
   
    thingssensors = Thingssensors.objects.filter(id_thing = thing.id).distinct()
    thingssensors = thingssensors.order_by("-id")
    
    # Filter
    sensorslist = []
    chartview_label = None
    chartview_title = None
    lastdatum = None

    for thingsensor in thingssensors:
        id_sensor = thingsensor.id_sensor.id
        
        # Get unit select by user
        unit = request.COOKIES.get('unit' + str(id_sensor))
        chart = request.COOKIES.get('chart' + str(id_sensor))
        precision = request.COOKIES.get('precision' + str(id_sensor))
 
        if unit is None:
            sensorunit = Sensorsunits.objects.get(id_sensor = id_sensor, isdefault = True)
        else:
            sensorunit = Sensorsunits.objects.get(id = unit)

        if precision is None:
            precision = sensorunit.precision
        else:
            precision = int(precision)

        if chart is None:
            chart = CHART_DEFAULT
 
        # Check if is value or message
        if thingsensor.id == 3: #ID for Sensor Message
            data = Thingssensorsdata.objects.filter(id_thingsensor = thingsensor.id, value__isnull = True) \
                    .order_by('-dt')[:5]
 
            chart = 'table'
            lastdatum = None
        else:
            data = Thingssensorsdata.objects \
                    .filter(id_thingsensor = thingsensor.id, value__isnull = False)

            if data is None:
                chartview = None
            else:
                if chartview is None:
                    chartview = CHARTVIEW_DEFAULT

            # Datetime show data
            lastrecord = data.last()

            if lastrecord is not None:
                lastdatum = lastrecord.dtread.astimezone()
            else:
                chartview = None

            # Grouping data of sensor
            if chartview == 's':
                chartview_label = lastdatum.strftime("%d/%m/%Y %H:%M")
                chartview_title = 'Segundos'

                data = data.filter(dtread__year=lastdatum.year, \
                                   dtread__month=lastdatum.month, \
                                   dtread__day=lastdatum.day, \
                                   dtread__hour=lastdatum.hour, \
                                   dtread__minute=lastdatum.minute)
                
                data = data.values(group_dt=Extract('dtread', 'second')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'm':
                chartview_label = lastdatum.strftime("%d/%m/%Y %Hh")
                chartview_title = 'Minutos'

                data = data.filter(dtread__year = lastdatum.year, \
                                   dtread__month = lastdatum.month, \
                                   dtread__day = lastdatum.day, \
                                   dtread__hour = lastdatum.hour)

                data = data.values(group_dt=Extract('dtread', 'minute')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'h':
                chartview_label = lastdatum.strftime("%d/%m/%Y")
                chartview_title = 'Horas'

                data = data.filter(dtread__year = lastdatum.year, \
                                   dtread__month = lastdatum.month, \
                                   dtread__day = lastdatum.day)

                data = data.values(group_dt=Extract('dtread', 'hour')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'd':
                chartview_label = lastdatum.strftime("%m/%Y")
                chartview_title = 'Dias'

                data = data.filter(dtread__year = lastdatum.year, \
                                   dtread__month = lastdatum.month)

                data = data.values(group_dt=Extract('dtread', 'day')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'M':
                chartview_label = lastdatum.strftime("%Y")
                chartview_title = 'Meses'

                data = data.filter(dtread__year = lastdatum.year)

                data = data.values(group_dt=Extract('dtread', 'month')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'y':
                chartview_label = ''
                chartview_title = 'Anos'
 
                data = data.values(group_dt=Extract('dtread', 'year')) \
                        .annotate(group_value=Avg('value')) \
                        .order_by('group_dt', 'group_value')
            else:
                chartview_label = 'Sem Dados'
                chartview_title = 'Selecione Visualizacao'
            
            if chart == 'display':
                data = data.order_by('-group_dt')[:1]
            
            # Recalc values by expression
            for datum in data:
                pv = datum['group_value'] # Variable use in calc
                datum['group_value'] = round(eval(sensorunit.expression), precision)
     
        # Build dict sensor + unit
        sensorslist.append({
            'sensor': Sensors.objects.get(id = id_sensor),
            'type': chart,
            'label': chartview_label,
            'lastdatum': lastdatum,
            'unit': sensorunit,
            'data': data
        })

    context = {
        'thing': thing.name,
        'canva': 'chart-line',
        'chart_file': 'chart-line.js',
        'city': account.city,
        'state': account.state,
        'lastdatum': lastdatum,
        'title': chartview_title,
        'country': account.country,
        'access': access,
        'sensors': sensorslist,
        'tags': Thingstags.objects.filter(id_thing = thing.id)
    }
 
    return render(request, 'sensor.html', {'context': context})
'''

