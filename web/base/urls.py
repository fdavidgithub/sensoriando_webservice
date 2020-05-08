from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ListPublicSensors, name='home'),
    path('home', views.ListPublicSensors, name='home'),
    path('map', views.MapSensors, name='map'),
    path('www', views.RedirectSensoriando, name='www'),
    path('sensor/<int:id_thing>', views.SensorDetails, name='sensor'),
]


