from django.urls import path, include
from overview import views

#https://learndjango.com/tutorials/django-login-and-logout-tutorial
urlpatterns = [
    path('', views.Home, name='home'),

]

