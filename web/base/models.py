from django.db import models

# Create your models here.
class Category(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)


