from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Avg, Value, CharField
from django.db.models.functions import Extract, Concat
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.response import Response
from .legacy_tables import Things, Thingstags, Thingssensors, Accounts, Accountsthings, Sensors, Sensorsunits, \
                           Thingssensorsdata, Plans
from .forms import SignUpForm, AccountForm, UserForm, ThingForm

from .constants import CHART_DEFAULT, CHARTVIEW_DEFAULT, MAX_PRECISION
import unicodecsv, datetime

import requests

def callAPI(endpoint):
    try:
        response = requests.get(settings.PREFIX_API + endpoint)
    
        if response.status_code == 200:
            return response.json()
        else:
            return Response({'warning': 'Invalid request: ' + str(response.status_code)})
    except:
        return Response({'error': 'Bad request: ' + settings.PREFIX_API + endpoint})
        
#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def SignUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            city    = form.cleaned_data.get('city')
            state   = form.cleaned_data.get('state')
            country = form.cleaned_data.get('country')
     
            plan = Plans.objects.get(id = 1)

            account = djAccount(
                        dt=datetime.datetime.today(),
                        username=user.username,
                        city=city, 
                        state=state, 
                        country=country, 
                        id_plan=plan, 
                        status=True
                      )
            account.save()

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


#@csrf_exempt
#def topics(request):
    # Monta resposta em CSV
#    response = HttpResponse(content_type='text/csv')
#    writer = unicodecsv.writer(response, encoding='UTF-8')

#    valid = Accounts.objects.filter(username=request.POST.get("username"), 
#                                   password=request.POST.get("password"),
#                                  )
    
#    regs = Sensors.objects.filter(user_ptr_id=valid[0].user_ptr_id)

#    for r in regs:
#        name="{}/{}".format(r.id_local, r.name)
#        row = [r.id, name, r.token]

#        writer.writerow(row)

#    return response

#@csrf_exempt
#def export_csv(request):
    # Monta resposta em CSV
#    response = HttpResponse(content_type='text/csv')
#    writer = unicodecsv.writer(response, encoding='UTF-8')

#    valid = Accounts.objects.filter(username=request.POST.get("username"), 
#                                   password=request.POST.get("password"),
#                                  )
    
#    regs = Sensors.objects.filter(user_ptr_id=valid[0].user_ptr_id)

#    for r in regs:
#        name="{}/{}".format(r.id_local, r.name)
#        row = [r.id, name, r.token]

#        writer.writerow(row)

#    return response

def ListPrivateSensors(request):
    if not request.user.is_authenticated:
        return redirect('/home')

    account = Accounts.objects.get(username = request.user.username)

    accountsthings = Accountsthings.objects.filter(id_account = account.id)
    ids_thing = accountsthings.values_list('id_thing', flat=True)

    id_plan = account.id_plan.id 
    plans = Plans.objects.get(id = id_plan)

    thingssensors = Thingssensors.objects.filter(id_thing__in = ids_thing)
    ids_thingsensor = thingssensors.values_list('id', flat=True)

    records = Thingssensorsdata.objects.filter(id_thingsensor__in = ids_thingsensor).count()

    datalist = []
    things = Things.objects.filter(id__in = ids_thing)
       
    for thing in things:
        thingssensors = Thingssensors.objects.filter(id_thing = thing.id)
        thingsensor_ids = thingssensors.values_list('id', flat=True)

        try:
            thingdatum = Thingssensorsdata.objects.filter(id_thingsensor__in = thingsensor_ids).latest('id')
            last_update = thingdatum.dt
        except:
            last_update = 'nenhuma'

        sensors_ids = thingssensors.values_list('id_sensor', flat=True)
        sensors = Sensors.objects.filter(id__in = sensors_ids)

        datalist.append({
            'id': thing.id,
            'name': thing.name,
            'nameslug': thing.name.replace(" ", "-"),
            'city': account.city,
            'cityslug': account.city.replace(" ", "-"),
            'state': account.state,
            'country': account.country,
            'last_update': last_update,
            'tags': Thingstags.objects.filter(id_thing = thing.id),
            'sensors': sensors,
        })

    if records > 1000000:
        records = records/1000000
        rec_unit = 'M'
    elif records > 1000:
        records = records/1000
        rec_unit = 'K'
    else:
        rec_unit = ''

    retation_current = round(records/60/60/24/30, 2)

    if plans.retation > 1:
        ret_unit = 'meses'
    else:
        ret_unit = 'mes'
        
    contexts = {
        'data': datalist,
        'records': records,
        'rec_unit': rec_unit,
        'retation_current': retation_current,
        'retation_full': plans.retation,
        'ret_unit': ret_unit,
    }
           
    return render(request, 'home.html', {'contexts': contexts})

def ListPublicSensors(request, filterparam=None):
    plans = Plans.objects.filter(ispublic = True)
    accounts = Accounts.objects.filter(id_plan__in = plans)

    filterapply = ''
    if filterparam is not None:
        filterparam = filterparam.replace('-', ' ')
        query=dict(e.split('=') for e in filterparam.split('&'))
        
        if "city" in query:
            filterapply = query['city']
            accounts = accounts.filter(city = filterapply)

        if "state" in query:
            filterapply = query['state']
            accounts = accounts.filter(state = filterapply)
        
        if "country" in query:
            filterapply = query['country']
            accounts = accounts.filter(country = filterapply)
    
    datalist = []
    for account in accounts:
#        accountsthings = Accountsthings(id_account = account.id)
#        accountthing_ids = accountsthings.values_list('id_thing', flat=True)

#        things = Things.objects.filter(id__in = accountthing_ids)
        things = Things.objects.filter(accountsthings__id_account = account.id)
        
        for thing in things:
            thingssensors = Thingssensors.objects.filter(id_thing = thing.id)
            thingsensor_ids = thingssensors.values_list('id', flat=True)
            
            try:
                thingdatum = Thingssensorsdata.objects.filter(id_thingsensor__in = thingsensor_ids).latest('id')
                last_update = thingdatum.dt
            except:
                last_update = None

            sensorlist = []
            sensors = Thingssensors.objects.filter(thingssensorsdata__id_thingsensor__in = thingsensor_ids).distinct()
            sensor_ids = sensors.values_list('id_sensor', flat=True)

            sensors = Sensors.objects.filter(id__in = sensor_ids)
            
            if filterparam is not None:
                if "sensor" in query:
                    filterapply = query['sensor']
                    sensors = sensors.filter(name = filterapply)
                
                if "flag" in query:
                    if "sensor" in query:
                        filterapply = query['sensor'] + ' e ' + query['flag']
                    else:
                        filterapply = query['flag']
 
                    thingstags = Thingstags.objects.filter(id_thing = thing.id, name = query['flag'])
                    thing_ids = thingstags.values_list('id_thing', flat=True)
                    
                    thingssensors = Thingssensors.objects.filter(thingssensorsdata__id_thing__in = thing_ids)
                    thingssensors_ids = thingssensors.values_list('id_sensor', flat=True)

                    sensors = Sensors.objects.filter(id__in = thingssensors_ids)

            if sensors:
                datalist.append({
                    'id': thing.id,
                    'nameslug': thing.name.replace(" ", "-"),
                    'name': thing.name,
                    'city': account.city,
                    'cityslug': account.city.replace(" ", "-"), 
                    'state': account.state,
                    'country': account.country,
                    'last_update': last_update,
                    'tags': Thingstags.objects.filter(id_thing = thing.id),
                    'sensors': sensors,
                })

    contexts = {
        'searchtags': Thingstags.objects.all().distinct(),
        'searchsensors': Sensors.objects.all(),
        'filterapply': filterapply, 
        'data': datalist
    }

    return render(request, 'home.html', {'contexts': contexts})

def MapSensors(request):
    accounts = Accounts.objects.values('country').order_by('country').annotate(total=Count('country'))
    contexts = {
        'countries': accounts, 
    }

    return render(request, 'map.html', {'contexts': contexts})

def NotFound(request):
    contexts = []
    return render(request, '404.html', {'contexts': contexts})

def MyAccount(request, username, tab):
    try:
        account = Accounts.objects.get(username = username)
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect('/home')

    things = Things.objects.filter(accountsthings__id_account = account.id)
    things_ids = things.values_list('id', flat=True)

    thingssensors = Thingssensors.objects.filter(id_thing__in = things_ids).distinct()
    thingssensors_ids = thingssensors.values_list('id_sensor', flat=True)
    
    sensors = Sensors.objects.filter(id__in = thingssensors_ids)

    sensorlist = []
    for sensor in sensors:
        unitselect = request.COOKIES.get('unit' + str(sensor.id))
        if unitselect is not None:
            unitselect = int(unitselect)
 
        chartselect = request.COOKIES.get('chart' + str(sensor.id))
        if chartselect is None:
            chartselect = CHART_DEFAULT

        precisionselect = request.COOKIES.get('precision' + str(sensor.id))
        if precisionselect is None:
            precisionselect = Sensorsunits.objects.get(isdefault = True, id_sensor = sensor.id).precision
        else:
            precisionselect = int(precisionselect)
        
        sensorlist.append({
            'name': sensor.name,
            'id': sensor.id,
            'unitselect': unitselect,
            'chartselect': chartselect,
            'precisionselect': precisionselect,
            'units': Sensorsunits.objects.filter(id_sensor = sensor.id)
        })

    if request.method == 'POST' and 'profileform' in request.POST:
        userform = UserForm(request.POST, instance=user)
 
        if userform.is_valid():
            userform.save()
    else:
        userform = UserForm(None, instance=user)
 
    if request.method == 'POST' and 'profileform' in request.POST:
        profileform = AccountForm(request.POST, instance=account)
 
        if profileform.is_valid():
            profileform.save()
    else:
        profileform = AccountForm(None, instance=account)

    if request.method == 'POST' and 'thingform' in request.POST:
        thingform = ThingForm(request.POST)

        if thingform.is_valid():
            uuid = thingform.cleaned_data.get('uuid')

            account = Accounts.objects.get(username = username)
            thing = Things.objects.get(uuid = uuid)

            accountthing = Accountsthings(
                            dt=datetime.datetime.today(),
                            id_thing=thing,
                            id_account=account
                           )
            accountthing.save()
#            thing.dt=datetime.datetime.today()
#            thing.id_thing=thing
#            thing.id_account=account
#            thing.save()
            return redirect('/account/' + username + '/things')
        else:
            tab = 'things'
    else:
        thingform = ThingForm()
 
    form = {
        'user': userform,
        'profile': profileform,
        'thing': thingform,
        'precision': range(MAX_PRECISION),
        'active': tab,
        'things': things,
        'sensors': sensorlist
    }

    return render(request, 'account.html', {'form': form})

def RedirectSensoriando(request):
    return redirect('http://www.sensoriando.com.br')

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


