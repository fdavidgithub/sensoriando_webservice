from rest_framework import viewsets
from . import serializers
from . import models

class ThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingSerializer
    queryset  = models.Things.objects.all()

class SensorViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorSerializer
    queryset  = models.Sensors.objects.all()

class TagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.TagSerializer
    queryset  = models.Thingssensorstags.objects.all()

