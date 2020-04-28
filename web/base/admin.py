from django.contrib import admin
from .models import Accounts, Things, Sensors

# Register your models here.
admin.site.register(Accounts)
admin.site.register(Things)
admin.site.register(Sensors)

