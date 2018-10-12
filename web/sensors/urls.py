from django.urls import path
from . import views

urlpatterns = [
    path('', views.sensors, name='sensors'),
]
