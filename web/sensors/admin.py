from django.contrib import admin
from . models import Local, Sensor, Flag

# Register your models here.
admin.site.register(Local)
admin.site.register(Sensor)
admin.site.register(Flag)

