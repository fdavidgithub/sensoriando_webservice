from django.db import models


class Vwaccountsthings(models.Model):
    id_account = models.IntegerField(blank=True, null=True)
    dt_account = models.DateTimeField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    usetrigger = models.BooleanField(blank=True, null=True)
    ispublic = models.BooleanField(blank=True, null=True)
    id_thing = models.IntegerField(blank=True, null=True)
    dt_thing = models.DateTimeField(blank=True, null=True)
    thing = models.CharField(max_length=30, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    isrelay = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'vwaccountsthings'


class Vwaccountsthingssensorsunits(models.Model):
    id_account = models.IntegerField(blank=True, null=True)
    id_thing = models.IntegerField(blank=True, null=True)
    id_module= models.IntegerField(blank=True, null=True)
    id_modulesensor = models.IntegerField(blank=True, null=True)
    id_sensor = models.IntegerField(blank=True, null=True)
    id_sensorunit = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'vwaccountsthingsmodulessensorsunits'


