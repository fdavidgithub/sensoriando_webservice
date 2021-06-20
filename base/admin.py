from django.contrib import admin
from .models import djAccount, djThing, djSensor, djPlan

# Register your models here.
admin.site.register(djAccount)
admin.site.register(djThing)
admin.site.register(djSensor)
admin.site.register(djPlan)

