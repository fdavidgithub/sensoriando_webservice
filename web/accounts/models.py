from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
class Account(User):
    is_public = models.BooleanField(default=True)
    city = models.CharField(max_length=50)
    uf = models.CharField(max_length=2)

