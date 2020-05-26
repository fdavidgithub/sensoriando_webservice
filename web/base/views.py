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

from .legacy_tables import Things, Thingsdata, Thingsflags, Sensors, Accounts, Accountsthings, Sensorsunits
from .legacy_views import Vwthingsdata, Vwaccountsthingssensorsunits
from .models import Account

from .forms import SignUpForm, AccountForm, UserForm, ThingForm

from .constants import CHART_DEFAULT, CHARTVIEW_DEFAULT
import unicodecsv, datetime

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
                'flags': Thingsflags.objects.filter(id_thing = thing.id),
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
 
                    thingsflags = Thingsflags.objects.filter(id_thing = thing.id, name = query['flag'])
                    thing_ids = thingsflags.values_list('id_thing', flat=True)
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
                    'flags': Thingsflags.objects.filter(id_thing = thing.id),
                    'sensors': sensors,
                })

    contexts = {
        'searchflags': Thingsflags.objects.all().distinct(),
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

def MyAccount(request, username):
    account = Accounts.objects.get(username = username)
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

        sensorlist.append({
            'name': sensor.name,
            'id': sensor.id,
            'unitselect': unitselect,
            'chartselect': chartselect,
            'units': Sensorsunits.objects.filter(id_sensor = sensor.id)
        })

    form = {
        'user': AccountUser(request, username),
        'profile': AccountProfile(request, username),
        'uuid': AccountThing(request, username),
        'things': things,
        'sensors': sensorlist
    }

    return render(request, 'account.html', {'form': form})

def AccountThing(request, username):
    if request.method == 'POST':
        thing = ThingForm(request.POST)

        if thing.is_valid():
            uuid = thing.cleaned_data.get('uuid')

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

#            return redirect('/account/' + username + '#things')
    else:
        thing = ThingForm()

    return thing

def AccountUser(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        return redirect('/404')
    
    userform = UserForm(request.POST or None, instance=user)
    
    if userform.is_valid():
        userform.save()
#        return redirect('/account/' + username)

    return userform

def AccountProfile(request, username):
    try:
        account = Accounts.objects.get(username=username)
    except:
        return redirect('/404')

    profile = AccountForm(request.POST or None, instance=account)
    
    if profile.is_valid():
        profile.save()
#        return redirect('/account/' + username)

    return profile

def RedirectSensoriando(request):
    return redirect('http://www.sensoriando.com.br')

def SensorDetails(request, id_thing):
    # Get from cookies
    chartview = request.COOKIES.get('chartview')
   
    # Get data
    thing = Things.objects.get(id = id_thing)
    account = Accounts.objects.get(accountsthings__id_thing = id_thing)
    sensors = Sensors.objects.filter(thingsdata__id_thing = id_thing).distinct()
    
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
 
        if sensorunit is None:
            sensorunit = Sensorsunits.objects.get(id_sensor = sensor.id, isdefault = True)
        else:
            sensorunit = Sensorsunits.objects.get(id = sensorunit)

        if sensorchart is None:
            sensorchart = CHART_DEFAULT

        # Get data o sensor
        data = Vwthingsdata.objects.filter(id_thing = thing.id, id_sensor = sensor.id)

        # Grouping data of sensor
        if data: 
            if chartview is None:
                chartview = CHARTVIEW_DEFAULT
        else:
            chartview = None
 
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
            chartview_label = 'ops!!!'
            chartview_title = 'ops!!!'
 
        # Recalc to convert
        for datum in data:
            pv = datum['group_value'] # Payload value
            datum['group_value'] = round(eval(sensorunit.expression), sensorunit.precision)

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
        'flags': Thingsflags.objects.filter(id_thing = id_thing)
    }

    return render(request, 'sensor.html', {'context': context})


