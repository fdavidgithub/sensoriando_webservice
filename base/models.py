from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.legacy_tables import *
from base.legacy_views import *

class ThingsTagsModel(Thingstags):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ThingTag"
        verbose_name_plural = 'ThingTags'
        proxy = True        

class ThingsSensorsTagsModel(Thingssensorstags):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "SensorTag"
        verbose_name_plural = 'SensorTags'
        proxy = True        

class SensorsUnitsModel(Sensorsunits):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = 'Units'
        proxy = True        

class PlansModel(Plans):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = 'Plans'
        proxy = True        

class AccountsModel(Accounts):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = 'Accounts'
        proxy = True       

class AccountsThingsModel(Accountsthings):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "AccountThing"
        verbose_name_plural = 'AccountThings'
        proxy = True  

class ThingsModel(Things):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Thing"
        verbose_name_plural = 'Things'
        proxy = True        

class ThingsTagsModel(Thingstags):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ThingTag"
        verbose_name_plural = 'ThingTags'
        proxy = True        

class SensorsModel(Sensors):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = 'Sensors'
        proxy = True   

class ThingsSensorsTagsModel(Thingssensorstags):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ThingSensorTag"
        verbose_name_plural = 'ThingSensorTags'
        proxy = True  

class ThingsSensorsModel(Thingssensors):
    class Meta:
        verbose_name = "ThingSensor"
        verbose_name_plural = 'ThingSensors'
        proxy = True  

class AccountsThingsModel(Accountsthings):
    class Meta:
        verbose_name = "AccountThing"
        verbose_name_plural = 'AccountThings'
        proxy = True  

class ThingsSensorsDataModel(Thingssensorsdata):
    class Meta:
        verbose_name = "ThingSensorDatum"
        verbose_name_plural = 'ThingSensorsData'
        proxy = True  

class DailyAverageDataModel(Dailyaveragedata):
    class Meta:
        verbose_name = "DailyAverageDatum"
        verbose_name_plural = 'DailyAverageData'
        proxy = True  

class MonthlyAverageDataModel(Monthlyaveragedata):
    class Meta:
        verbose_name = "MonthlyAverageDatum"
        verbose_name_plural = 'MonthlyAverageData'
        proxy = True  

class YearlyAverageDataModel(Yearlyaveragedata):
    class Meta:
        verbose_name = "YearlyAverageDatum"
        verbose_name_plural = 'YearlyAverageData'
        proxy = True  

class vwThingsSensorsData_YearModel(vwThingssensorsdata_year):    
    class Meta:
        verbose_name = "ThingSensorDatum_year"
        verbose_name_plural = 'ThingSensorsData_years'
        proxy = True  

class vwThingsSensorsData_MonthModel(vwThingssensorsdata_month):    
    class Meta:
        verbose_name = "ThingSensorDatum_month"
        verbose_name_plural = 'ThingSensorsData_months'
        proxy = True 

class vwThingsSensorsData_DayModel(vwThingssensorsdata_day):    
    class Meta:
        verbose_name = "ThingSensorDatum_day"
        verbose_name_plural = 'ThingSensorsData_days'
        proxy = True  
