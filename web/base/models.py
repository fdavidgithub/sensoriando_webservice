# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User 

# Gerador de senhas no tamanho especificado
#
def generate_token():
    chars = "ABCDEFGHIJMNOPQRSTUVXZabcdefghijmnopqrstuvxz1234567890"
    from os import urandom
    return "".join(chars[c % len(chars)] for c in urandom(32))

class Account(User):
    dt = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)
    is_public = models.BooleanField(default=True)
    status = models.BooleanField(default=True)
    dt_status = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'account'

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Category(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=5, blank=True, null=True)
    precision = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'
    
    def __str__(self):
        return self.name


class Data(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    id_sensor = models.ForeignKey('Sensor', models.DO_NOTHING, db_column='id_sensor')
    dt_stream = models.DateTimeField()
    value = models.FloatField()
    payload = models.CharField(max_length=32)

    class Meta:
        managed = False
        db_table = 'data'


class Flag(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    id_sensor = models.ForeignKey('Sensor', models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'flag'

    def __str__(self):
        return self.name


class Local(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    user_ptr_id = models.ForeignKey(Account, models.DO_NOTHING, db_column='user_ptr_id')

    class Meta:
        managed = False
        db_table = 'local'

    def __str__(self):
        return self.name


class Sensor(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    user_ptr_id = models.ForeignKey(Account, models.DO_NOTHING, db_column='user_ptr_id')
    id_local = models.ForeignKey(Local, models.DO_NOTHING, db_column='id_local')
    id_category = models.ForeignKey(Category, models.DO_NOTHING, db_column='id_category')
    name = models.CharField(max_length=30)
    token = models.CharField(max_length=32,default=generate_token)

    class Meta:
        managed = False
        db_table = 'sensor'

    def __str__(self):
        return self.name


