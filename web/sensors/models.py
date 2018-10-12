from django.db import models
from accounts.models import Account
from base.models import Category

# Create your models here.
class Local(Account):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)

class Sensor(Account):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    localized = models.ForeignKey(Local, on_delete=models.PROTECT)
 
class Flag(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

class Data(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

