from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from django import forms
from django.contrib.auth.forms import UserCreationForm

from rest_framework_simplejwt.tokens import AccessToken

import datetime
import os

from base.models import AccountsModel, AccountsThingsModel, ThingsModel, PlansModel, ThingsSensorsModel, SensorsModel, \
                        SensorsUnitsModel
from users.forms import SignUpForm, AccountForm, UserForm, ThingForm
from base.views import callAPI

CHART_DEFAULT = 'chart-line'
MAX_PRECISION = 3

class CustomSignIn(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'font-16px'})
        self.fields['password'].widget.attrs.update({'class': 'font-16px'})

class CustomSignUn(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'font-17px'})
        self.fields['password'].widget.attrs.update({'class': 'font-17px'})

# Create your views here.
#https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def SignUp(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            city    = form.cleaned_data.get('city')
            state   = form.cleaned_data.get('state')
            country = form.cleaned_data.get('country')
     
            plan = PlansModel.objects.get(id = 1)

            account = AccountsModel(
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

            return redirect('/home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

class SignIn(LoginView):
    template_name = 'signin.html'  # Especifique o caminho para o seu template
    form_class = CustomSignIn      # Use o formulário personalizado

    def form_valid(self, form):
        # Chamando o método form_valid da classe pai para realizar a validação padrão do formulário
        response = super().form_valid(form)

        # Obtenção do token de acesso
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password) 
        
        if user is not None:
            getToken(username, password)
        else:
            # Trate a autenticação falha, se necessário
            pass

        return response

def MyAccount(request, username, tab):
    try:
        account = AccountsModel.objects.get(username = username)
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return redirect('/home')

    things = ThingsModel.objects.filter(accountsthings__id_account = account.id)
    things_ids = things.values_list('id', flat=True)

    thingssensors = ThingsSensorsModel.objects.filter(id_thing__in = things_ids).distinct()
    thingssensors_ids = thingssensors.values_list('id_sensor', flat=True)
    
    sensors = SensorsModel.objects.filter(id__in = thingssensors_ids)

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
            precisionselect = SensorsUnitsModel.objects.get(isdefault = True, id_sensor = sensor.id).precision
        else:
            precisionselect = int(precisionselect)
        
        sensorlist.append({
            'name': sensor.name,
            'id': sensor.id,
            'unitselect': unitselect,
            'chartselect': chartselect,
            'precisionselect': precisionselect,
            'units': SensorsUnitsModel.objects.filter(id_sensor = sensor.id)
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

            account = AccountsModel.objects.get(username = username)
            thing = ThingsModel.objects.get(uuid = uuid)

            accountthing = AccountsThingsModel(
                            dt=datetime.datetime.today(),
                            id_thing=thing,
                            id_account=account
                           )
            accountthing.save()
#            thing.dt=datetime.datetime.today()
#            thing.id_thing=thing
#            thing.id_account=account
#            thing.save()
            return redirect('/users/account/' + username + '/things')
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

def getToken(user, password):
    access = None
    refresh = None

    jsonParams = {
        'username': user,
        'password': password,
    }

    jsonResult = callAPI(endpoint = "/token/" , data = jsonParams, method = "POST")
    if jsonResult:
        access = jsonResult["access"]
        refresh = jsonResult["refresh"]

    os.environ["TOKEN_ACCESS"] = access
    os.environ["TOKEN_REFRESH"] = refresh

def checkToken():
    valid = True
    
    jsonParams = {
        'token': os.environ["TOKEN_ACCESS"],

    }

    jsonResult = callAPI(endpoint = "/token/verify/" , data = jsonParams, method = "POST")  

    if not jsonResult:
        valid = False

    return valid

def refreshToken():
    jsonParams = {
        'refresh': os.environ["TOKEN_REFRESH"],

    }

    jsonResult = callAPI(endpoint = "/token/refresh/" , data = jsonParams, method = "POST")
    if jsonResult:
        os.environ["TOKEN_ACCESS"] = jsonResult["access"]

def check_and_refresh_token():
    try:
        if not checkToken():
            refreshToken()
    except Exception:
        redirect('/users/login')

    return os.environ["TOKEN_ACCESS"]


