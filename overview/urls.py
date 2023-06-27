from django.urls import path, include
from overview import views

#https://learndjango.com/tutorials/django-login-and-logout-tutorial
urlpatterns = [
    path('', views.Public, name='home'),
    path('home/', views.Public, name='home'),
    path('home/private', views.Private, name='private'),

]

