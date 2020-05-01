from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ListPublicSensors, name='home'),
    path('home', views.ListPublicSensors, name='home'),
    path('search', views.SearchPublicSensors, name='search'),
    path('www', views.RedirectSensoriando, name='www'),
    path('sensor/<int:id_thing>', views.SensorDetails, name='sensor'),
]


