from rest_framework import serializers
from . import models

class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Things
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensors
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Thingssensorstags
        fields = '__all__'


