from django.urls import path, include
from . import views

#https://learndjango.com/tutorials/django-login-and-logout-tutorial
urlpatterns = [
    path('', views.ListPublicSensors, name='home'),
    path('home/search/<str:filterparam>', views.ListPublicSensors, name='home'),
    path('home', views.ListPublicSensors, name='home'),
    path('home/private', views.ListPrivateSensors, name='home'),
    path('map', views.MapSensors, name='map'),
    path('www', views.RedirectSensoriando, name='www'),
    path('sensor/<int:id_thing>', views.SensorDetails, name='sensor'),
    path('signup/', views.SignUp, name='signup'),
    path('account/<str:username>', views.MyAccount, name='account'),
]


