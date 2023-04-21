from api.views import *
from django.conf import settings

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


