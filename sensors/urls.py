from django.urls import path, include
from sensors import views

#https://learndjango.com/tutorials/django-login-and-logout-tutorial
urlpatterns = [
    path('detail/<str:uuid>', views.ThingDetails, name='thingdetail'),

]

