# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accounts(models.Model):
    dt = models.DateTimeField()
    username = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=20)
    ispublic = models.BooleanField()
    status = models.BooleanField()
    usetrigger = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts'

class Things(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(max_length=30)
    uuid = models.UUIDField(unique=True)
    isrelay = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'things'

class Sensors(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'sensors'


class Accountsthings(models.Model):
    dt = models.DateTimeField()
    id_account = models.ForeignKey(Accounts, models.DO_NOTHING, db_column='id_account')
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'accountsthings'


class Sensorsparams(models.Model):
    dt = models.DateTimeField()
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')

    class Meta:
        managed = False
        db_table = 'sensorsparams'
        unique_together = (('id_sensor', 'key'),)


class Sensorsunits(models.Model):
    dt = models.DateTimeField()
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(unique=True, max_length=50)
    initial = models.CharField(max_length=5, blank=True, null=True)
    precision = models.SmallIntegerField(blank=True, null=True)
    isdefault = models.BooleanField()
    expression = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensorsunits'
        unique_together = (('id_sensor', 'name'),)



class Thingsdata(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    qos = models.IntegerField()
    retained = models.BooleanField()
    payload = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'thingsdata'
        unique_together = (('id_thing', 'id_sensor', 'payload'),)


class Thingsflags(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'thingsflags'
        unique_together = (('id_thing', 'name'),)


class Thingsparams(models.Model):
    dt = models.DateTimeField()
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'thingsparams'
        unique_together = (('id_thing', 'key'),)


