from django.contrib import admin
from .models import Account, Thing, Sensor, Accountsthings, Thingssensorsdata

# Register your models here.
admin.site.register(Account)
admin.site.register(Thing)
admin.site.register(Sensor)
admin.site.register(Accountsthings)
admin.site.register(Thingssensorsdata)

