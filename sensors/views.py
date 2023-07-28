from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

from base.views import callAPI
from users.views import check_and_refresh_token
from base.models import ThingsModel, AccountsModel, PlansModel, ThingsSensorsModel, ThingsTagsModel

from dateutil.parser import parse
import pandas as pd
import json

def ThingDetails(request, uuid = None):
    dateFormats = {
        'second': {'label': '%d/%m/%Y %H:%M', 'legend': '%S'},
        'minute': {'label': '%d/%m/%Y %Hh', 'legend': '%M'},
        'hour': {'label': '%d/%m/%Y', 'legend': '%H'},
        'day': {'label': '%m/%Y', 'legend': '%d'},
        'month': {'label': '%Y', 'legend': '%m'},
        'year': {'label': '', 'legend': '%Y'}
    }

    # Get from cookies
    try:
        chartView = request.COOKIES.get('chartview')
    except:
        chartView = 'second'

    # Get data
    thing = ThingsModel.objects.get(uuid = uuid)
    thingtags = ThingsTagsModel.objects.filter(id_thing = thing.id)
    thingssensors = ThingsSensorsModel.objects.filter(id_thing = thing.id)
    account = AccountsModel.objects.get(accountsthings__id_thing = thing.id)
 
    tags = []
    for tag in thingtags:
        tags.append(tag.name)

    sensors = []
    for thingsensor in thingssensors:
        try:
            charttype = request.COOKIES.get('chart' + str(id_sensor))
        except:
            chartType = 'line'

        try:
            chartUnit = request.COOKIES.get('unit' + str(id_sensor))
        except:
            chartUnit = '???' 

        sensor = thingsensor.id_sensor.name

        jsonParams = {
            'thing': uuid,
            'sensor': sensor,
            'period': chartView,

        }
    
        if account.id_plan.ispublic:
            jsonResult = callAPI(
                endpoint = "/data/detail/", \
                data = jsonParams, \
                method = "POST"
            )
        else:
            jsonResult = callAPI(
                endpoint = "/data/detail/private/", \
                data = jsonParams, \
                method = "POST", \
                token = check_and_refresh_token()
            )

        # Precisa melhorar isso
        try:
            len(jsonResult)
        except:
            jsonResult = None
        ####

        if jsonResult: 
            lastDatum = parse(jsonResult[-1]['dtread'])
            chartLabel = lastDatum.strftime(dateFormats[chartView]['label'])

            for read in jsonResult:
                dtPart = parse(read['dtread'])
                read['dtread'] = dtPart.strftime(dateFormats[chartView]['legend'])

            #Grouping values
            df = pd.DataFrame(jsonResult)                                   #Panda: Convert json to DataFrame
            df["value"] = df.groupby("dtread")["value"].transform("mean")   #Panda: Calc average
            processedData = df.to_dict("records")                           #Panda: Convert DataFrame to Dict
        
            sensors.append({
                'name': sensor,
                'type': chartType,
                'label': chartLabel,
                'lastdatum': lastDatum,
                'unit': chartUnit,
                'data': processedData,

            })

    context = {
        'thing': thing.name,
        'thing_tags': tags,
        'canva': 'chart-line',
        'chart_file': 'chart-line.js',
        'city': account.city,
        'state': account.state,
        'title': chartView,
        'country': account.country,
        'sensors': sensors,

    }

    return render(request, 'sensor.html', {'context': context})

