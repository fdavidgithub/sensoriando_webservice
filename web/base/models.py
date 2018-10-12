from django.db import models
from django.contrib.auth.models import User 

from django.contrib.auth.forms import UserCreationForm

# Create your models here.
class Category(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)

class Account(User):
    is_public = models.BooleanField(default=True)
    city = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)

class account_signup(UserCreationForm):
    class meta: 
        model = Account

##
class Local(Account):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)

###
class Sensor(Account):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    localized = models.ForeignKey(Local, on_delete=models.PROTECT)
 
####
class Flag(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

class Data(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

