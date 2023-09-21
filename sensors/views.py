from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

from base.views import callAPI
from users.views import check_and_refresh_token
from base.models import ThingsModel, AccountsModel, PlansModel, ThingsSensorsModel, ThingsTagsModel, SensorsUnitsModel

from dateutil.parser import parse
import pandas as pd
import json

def ThingDetails(request, uuid = None):
    defaults = {
        "charttype": 'line',
        "chartview": "second",
 
    }

    dateFormats = {
        'second': {'label': '%d/%m/%Y %H:%M', 'legend': '%S'},
        'minute': {'label': '%d/%m/%Y %Hh', 'legend': '%M'},
        'hour': {'label': '%d/%m/%Y', 'legend': '%H'},
        'day': {'label': '%m/%Y', 'legend': '%d'},
        'month': {'label': '%Y', 'legend': '%m'},
        'year': {'label': '', 'legend': '%Y'},

    }

    chartView = defaults['chartview']

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
        id_sensor = thingsensor.id_sensor_id
        sensor = thingsensor.id_sensor.name
        sensor_unit = SensorsUnitsModel.objects.get(isdefault = True, id_sensor = id_sensor)

        defaults["chartunit"] = sensor_unit
        defaults["chartprecision"] = sensor_unit.precision
 
        # Get from cookies
        try:
            chartView = request.COOKIES.get('chartview')

            if not chartView:
                chartView = defaults['chartview']
        except:
            chartView = defaults['chartview']

        try:
            chartType = request.COOKIES.get('chart' + str(id_sensor))

            if not chartType:
                chartType = defaults['charttype']
        except:
            chartType = defaults['charttype']
    
        try:
            chartPrecision = int(request.COOKIES.get('precision' + str(id_sensor)))
        
            if not chartPrecision:
                chartPrecision = defaults['chartprecision']
        except:
            chartPrecision = defaults['chartprecision']

        try:
            id_unit = request.COOKIES.get('unit' + str(id_sensor))
            chartUnit = SensorsUnitsModel.objects.get(id = id_unit)

            if not chartUnit:
                chartUnit = defaults['chartunit']
        except:
            chartUnit = defaults['chartunit']

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
            df.eval("value = " + chartUnit.expression.replace("pv", "value"), \
                    inplace = True)                                         #Panda: Math Expression
            df["value"] = df["value"].round(chartPrecision)
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
        'chart_file': 'chart.js',
        'city': account.city,
        'state': account.state,
        'title': chartView,
        'country': account.country,
        'sensors': sensors,

    }

    return render(request, 'sensor.html', {'context': context})

