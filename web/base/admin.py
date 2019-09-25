from django.contrib import admin
from .models import Account, Category, Local, Sensor, Flag

# Register your models here.
admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Local)
admin.site.register(Sensor)
admin.site.register(Flag)

