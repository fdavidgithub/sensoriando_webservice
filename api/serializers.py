from rest_framework import serializers
from api import models

class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Things
        fields = ('name',  
        
        )

class ThingTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Thingstags
        fields = ('name',
        
        )

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensors
        fields = ('name',
        
        )

class SensorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Thingssensorstags
        fields = ('name',
        
        )

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Accounts
        fields = ('username',
                  'city',
                  'state',
                  'country',
       
        )

class AccountThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Accountsthings
        fields = ('id_thing',
#                  'sensors',
#                  'tags',

        )


class AccountThingSensorTagSerializer(serializers.ModelSerializer):
#    sensors = SensorSerializer(many = True, read_only = True)
#    tags = ThingTagSerializer(many = True, read_only = True)

    class Meta:
        model = models.Accountsthings
        fields = ('id_thing',
#                  'sensors',
#                  'tags',

        )



