from rest_framework import serializers
from . import models

class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Things
        fields = '__all__'
