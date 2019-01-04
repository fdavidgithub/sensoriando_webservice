from django.db import models
from accounts.models import Account
from base.models import Category

# Create your models here.
class Local(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Sensor(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    local = models.ForeignKey(Local, on_delete=models.PROTECT)
 
    def __str__(self):
        return self.name

class Flag(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class Data(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT)

