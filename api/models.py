from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .legacy_tables import *
from .legacy_views import *

class apiPlan(Plans):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = 'Plans'
        proxy = True        

class apiAccount(Accounts):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = 'Accounts'
        proxy = True        

class apiThing(Things):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Thing"
        verbose_name_plural = 'Things'
        proxy = True        

class apiSensor(Sensors):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = 'Sensors'
        proxy = True   


