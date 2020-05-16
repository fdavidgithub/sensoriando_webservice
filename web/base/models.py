from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .legacy_tables import *
from .legacy_views import *

#class Account(Accounts):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)
#
#    def __init__(self, *args, **kwargs):
#        self._meta.get_field('dt').default = datetime.datetime.today()
#        self._meta.get_field('status').default = True
#        self._meta.get_field('ispublic').default = True
#        self._meta.get_field('usetrigger').default = False
#        self.instance._state.adding = False
#    
#    def __str__(self):
#        return self.city
#
#    class Meta:
#        verbose_name_plural = 'Profile'
#        proxy = True        

