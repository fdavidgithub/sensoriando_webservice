from rest_framework import serializers
from . import models

class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Things
        fields = ('name',  
        )

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensors
        fields = ('name',
        )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Thingssensorstags
        fields = ('name',
        )


