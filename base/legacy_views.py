from django.db import models
from base.legacy_tables import Thingssensors

class vwThingssensorsdata_year(models.Model):
    timestamp_period = models.DateTimeField()
    dtread = models.DateTimeField()
    message = models.CharField(max_length=256, blank=True, null=True)
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vwthingssensorsdata_year'
      
class vwThingssensorsdata_month(models.Model):
    timestamp_period = models.DateTimeField()
    dtread = models.DateTimeField()
    message = models.CharField(max_length=256, blank=True, null=True)
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vwthingssensorsdata_month'
     
class vwThingssensorsdata_day(models.Model):
    timestamp_period = models.DateTimeField()
    dtread = models.DateTimeField()
    message = models.CharField(max_length=256, blank=True, null=True)
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vwthingssensorsdata_day'

