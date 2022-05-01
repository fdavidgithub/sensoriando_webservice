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
    id_plan = models.ForeignKey('Plans', models.DO_NOTHING, db_column='id_plan')
    username = models.CharField(unique=True, max_length=20)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=2)
    status = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts'


class Accountsthings(models.Model):
    dt = models.DateTimeField()
    id_account = models.ForeignKey(Accounts, models.DO_NOTHING, db_column='id_account')
    id_thing = models.ForeignKey('Things', models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'accountsthings'
        unique_together = (('id_account', 'id_thing'),)


class Connections(models.Model):
    dt = models.DateTimeField()
    qos = models.IntegerField()
    retained = models.BooleanField()
    topic = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'connections'
        unique_together = (('qos', 'retained', 'topic'),)


class Payloads(models.Model):
    dt = models.DateTimeField()
    id_connection = models.ForeignKey(Connections, models.DO_NOTHING, db_column='id_connection')
    payload = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'payloads'
        unique_together = (('id_connection', 'payload'),)


class Plans(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(unique=True, max_length=30)
    ispublic = models.BooleanField()
    istrigger = models.BooleanField()
    retation = models.IntegerField()
    vlhour = models.FloatField()
    vltrigger = models.FloatField()
    visible = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'plans'


class Sensors(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'sensors'


class Sensorsunits(models.Model):
    dt = models.DateTimeField()
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(unique=True, max_length=50)
    initial = models.CharField(max_length=5, blank=True, null=True)
    precision = models.SmallIntegerField(blank=True, null=True)
    isdefault = models.BooleanField()
    expression = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensorsunits'


class Things(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(max_length=30)
    uuid = models.UUIDField(unique=True)
    isrelay = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'things'


class Thingsparams(models.Model):
    dt = models.DateTimeField()
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'thingsparams'
        unique_together = (('id_thing', 'key'),)


class Thingssensors(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')

    class Meta:
        managed = False
        db_table = 'thingssensors'


class Thingssensorsdata(models.Model):
    dt = models.DateTimeField()
    id_payload = models.ForeignKey(Payloads, models.DO_NOTHING, db_column='id_payload')
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    dtread = models.DateTimeField()
    value = models.FloatField(blank=True, null=True)
    message = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thingssensorsdata'
        unique_together = (('id_payload', 'id_thingsensor'),)


class Thingssensorsparams(models.Model):
    dt = models.DateTimeField()
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'thingssensorsparams'
        unique_together = (('id_thingsensor', 'key'),)


class Thingssensorstags(models.Model):
    dt = models.DateTimeField()
    id_thingsensor = models.ForeignKey(Thingssensors, models.DO_NOTHING, db_column='id_thingsensor')
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'thingssensorstags'
        unique_together = (('id_thingsensor', 'name'),)


class Thingstags(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'thingstags'
        unique_together = (('id_thing', 'name'),)
