import requests

def ListPublicSensors(sensor=None, tag=None):
    data = []
    api_url="http://localhost:8000"
    
    public = requests.get(api_url + "/apiaccountthingsensortag/").json()
    
    for public in publics:
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


