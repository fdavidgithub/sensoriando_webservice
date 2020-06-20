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

from .legacy_tables import Things, Thingsdata, Thingstags, Sensors, Accounts, Accountsthings, Sensorsunits
from .legacy_views import Vwthingsdata, Vwaccountsthingssensorsunits
from .models import Account

from .forms import SignUpForm, AccountForm, UserForm, ThingForm

from .constants import CHART_DEFAULT, CHARTVIEW_DEFAULT, MAX_PRECISION
import unicodecsv, datetime, pytz

#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def SignUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            city    = form.cleaned_data.get('city')
            state   = form.cleaned_data.get('state')
            country = form.cleaned_data.get('country')
       
            account = Account(
                        dt=datetime.datetime.today(),
                        username=user.username,
                        city=city, 
                        state=state, 
                        country=country, 
                        ispublic=True, 
                        status=True, 
                        usetrigger=False
                      )
            account.save()

            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


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

def ListPrivateSensors(request):
    if not request.user.is_authenticated:
        return redirect('/home')

    accounts = Accounts.objects.filter(username = request.user.username)
    
    datalist = []
    for account in accounts:
        things = Things.objects.filter(accountsthings__id_account = account.id)
       
        for thing in things:
            try:
                thingdatum = Thingsdata.objects.filter(id_thing = thing.id).latest('id')
                last_update = thingdatum.dt
            except:
                last_update = 'nenhuma'

            sensors = Sensors.objects.filter(thingsdata__id_thing = thing.id).distinct()

            datalist.append({
                'id': thing.id,
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
        'data': datalist
    }
           
    return render(request, 'home.html', {'contexts': contexts})

def ListPublicSensors(request, filterparam=None):
    accounts = Accounts.objects.filter(ispublic = True)

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
        things = Things.objects.filter(accountsthings__id_account = account.id)
       
        for thing in things:
            try:
                thingdatum = Thingsdata.objects.filter(id_thing = thing.id).latest('id')
                last_update = thingdatum.dt
            except:
                last_update = 'nenhuma'

            sensorlist = []
            sensors = Sensors.objects.filter(thingsdata__id_thing = thing.id).distinct()
            
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
                    sensors = sensors.filter(thingsdata__id_thing__in = thing_ids)
 
            if sensors:
                datalist.append({
                    'id': thing.id,
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
    sensors = Sensors.objects.filter(thingsdata__id_thing__in = things_ids).distinct()

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

def SensorDetails(request, id_thing):
    # Get from cookies
    chartview = request.COOKIES.get('chartview')
   
    # Get data
    thing = Things.objects.get(id = id_thing)
    account = Accounts.objects.get(accountsthings__id_thing = thing.id)
    sensors = Sensors.objects.filter(thingsdata__id_thing = thing.id).order_by('name').distinct()
    
    if account.ispublic:
        access = 'Publico'
    else:
        access = 'Privado'

    sensorslist = []
    chartview_label = None
    chartview_title = None

    for sensor in sensors:
        # Get unit select by user
        sensorunit = request.COOKIES.get('unit' + str(sensor.id))
        sensorchart = request.COOKIES.get('chart' + str(sensor.id))
        sensorprecision = request.COOKIES.get('precision' + str(sensor.id))
 
        if sensorunit is None:
            sensorunit = Sensorsunits.objects.get(id_sensor = sensor.id, isdefault = True)
        else:
            sensorunit = Sensorsunits.objects.get(id = sensorunit)

        if sensorprecision is None:
            sensorprecision = Sensorsunits.objects.get(id_sensor = sensor.id, isdefault = True).precision
        else:
            sensorprecision = int(sensorprecision)

        if sensorchart is None:
            sensorchart = CHART_DEFAULT
 
        # Check if is value or message
        if sensorunit.expression is None:
            sensorchart = 'table'
            data = Vwthingsdata.objects.filter(id_thing = thing.id, id_sensor = sensor.id, payload_value__isnull = True) \
                    .order_by('-dt_thingdatum')[:10]
        elif sensorchart == 'display':
            data = Vwthingsdata.objects.filter(id_thing = thing.id, id_sensor = sensor.id, payload_value__isnull = False) \
                    .last()
            chartview_label = data.payload_dt.strftime("%d/%m/%Y %H:%M:S")
        else:
            data = Vwthingsdata.objects.filter(id_thing = thing.id, id_sensor = sensor.id, payload_value__isnull = False) \
                    .order_by('-dt_thingdatum')

            lastdatum = data[0].payload_dt      #Last record
            lastdatum = lastdatum.astimezone()  #Set to current timezone

            # Grouping data of sensor        
            if data: 
                if chartview is None:
                    chartview = CHARTVIEW_DEFAULT
            else:
                chartview = None
    
            if chartview == 's':
                chartview_label = lastdatum.strftime("%d/%m/%Y %H:%M")
                chartview_title = 'Segundos'
 
                data = data.filter(payload_dt__year=lastdatum.year, \
                                   payload_dt__month=lastdatum.month, \
                                   payload_dt__day=lastdatum.day, \
                                   payload_dt__hour=lastdatum.hour, \
                                   payload_dt__minute=lastdatum.minute)

                data = data.values(group_dt=Extract('payload_dt', 'second')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')                
            elif chartview == 'm':
                chartview_label = lastdatum.strftime("%d/%m/%Y %Hh")
                chartview_title = 'Minutos'

                data = data.filter(payload_dt__year = lastdatum.year, \
                                   payload_dt__month = lastdatum.month, \
                                   payload_dt__day = lastdatum.day, \
                                   payload_dt__hour = lastdatum.hour)

                data = data.values(group_dt=Extract('payload_dt', 'minute')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'h':
                chartview_label = lastdatum.strftime("%d/%m/%Y")
                chartview_title = 'Horas'

                data = data.filter(payload_dt__year = lastdatum.year, \
                                   payload_dt__month = lastdatum.month, \
                                   payload_dt__day = lastdatum.day)

                data = data.values(group_dt=Extract('payload_dt', 'hour')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'd':
                chartview_label = lastdatum.strftime("%m/%Y")
                chartview_title = 'Dias'

                data = data.filter(payload_dt__year = lastdatum.year, \
                                   payload_dt__month = lastdatum.month)

                data = data.values(group_dt=Extract('payload_dt', 'day')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'M':
                chartview_label = lastdatum.strftime("%Y")
                chartview_title = 'Meses'

                data = data.filter(payload_dt__year = lastdatum.year)

                data = data.values(group_dt=Extract('payload_dt', 'month')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')
            elif chartview == 'y':
                chartview_label = ''
                chartview_title = 'Anos'
 
                data = data.values(group_dt=Extract('payload_dt', 'year')) \
                        .annotate(group_value=Avg('payload_value')) \
                        .order_by('group_dt', 'group_value')
            else:
                chartview_label = 'ops!!!'
                chartview_title = 'ops!!!'
 
            # Recalc to convert
            for datum in data:
                pv = datum['group_value'] # Payload value
                datum['group_value'] = round(eval(sensorunit.expression), sensorprecision)
        
       # Build dict sensor + unit
        sensorslist.append({
            'sensor': sensor,
            'type': sensorchart,
            'unit': sensorunit,
            'data': data
        })
    
    context = {
        'thing': thing.name,
        'canva': 'chart-line',
        'chart_file': 'chart-line.js',
        'city': account.city,
        'state': account.state,
        'label': chartview_label,
        'title': chartview_title,
        'country': account.country,
        'access': access,
        'sensors': sensorslist,
        'tags': Thingstags.objects.filter(id_thing = thing.id)
    }
 
    return render(request, 'sensor.html', {'context': context})


