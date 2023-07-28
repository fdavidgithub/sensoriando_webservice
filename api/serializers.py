from datetime import datetime

from django.db.models import Max
from rest_framework import serializers

from base.models import ThingsModel, ThingsTagsModel, SensorsModel, ThingsSensorsTagsModel, ThingsSensorsTagsModel, \
                        AccountsModel, AccountsThingsModel, ThingsSensorsModel, AccountsThingsModel, ThingsSensorsDataModel

class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThingsModel
        fields = ('uuid',
                  'name',  

        )

class ThingTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThingsTagsModel
        fields = ('name',
        
        )

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorsModel
        fields = ('id',
                  'name',
        )

class SensorTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThingsSensorsTagsModel
        fields = ('name',
        
        )

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountsModel
        fields = ('username',
                  'city',
                  'state',
                  'country',
       
        )

class DataThingsSerializer(serializers.ModelSerializer):
    thing = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()
    account = serializers.SerializerMethodField()
    sensors = serializers.SerializerMethodField()
    lastupdate = serializers.SerializerMethodField()
    thingtags = serializers.SerializerMethodField()

    class Meta:
        model = ThingsSensorsModel
        fields = ('thing', 'uuid', 'lastupdate', 'account', 'sensors', 'thingtags')
    
    def get_thing(self, obj):
        return obj.id_thing.name

    def get_uuid(self, obj):
        return obj.id_thing.uuid

    def get_account(self, obj):
        serializer = AccountSerializer(obj.id_account)
        return serializer.data

    def get_sensors(self, obj):
        #thing_sensors = ThingsSensorsModel.objects.filter(id_thing = obj.id_thing)
        #sensor_ids = [ts.id_sensor_id for ts in thing_sensors]
        sensor_ids = ThingsSensorsModel.objects.filter(id_thing = obj.id_thing).values_list("id_sensor_id", flat=True)

        sensors = SensorsModel.objects.filter(id__in = sensor_ids)
        return SensorSerializer(sensors, many = True).data

    def get_thingtags(self, obj):
        thing_tags = ThingsTagsModel.objects.filter(id_thing = obj.id_thing)
        return SensorSerializer(thing_tags, many = True).data

    def get_lastupdate(self, obj):
        thingsensor_ids = ThingsSensorsModel.objects.filter(id_thing = obj.id_thing)
        lastread = ThingsSensorsDataModel.objects.filter(id_thingsensor__in = thingsensor_ids).aggregate(Max('dtread'))['dtread__max']
       
        return lastread.strftime("%d/%m/%Y %H:%M:%S") if lastread else "---"

class DataStatsSerializer(serializers.Serializer):
    user = serializers.CharField()
    plan = serializers.CharField()
    records = serializers.IntegerField()
    record_unit = serializers.CharField()
    retation_current = serializers.IntegerField()
    retation_full = serializers.IntegerField()
    retation_unit = serializers.CharField()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        records = representation['records']  

        if representation["retation_full"] > 1:
            representation["retation_unit"] = 'meses'
        else:
            representation["retation_unit"] = 'mes'

        representation["retation_current"] = round(records/60/60/24/30, 2)
        
        if records > 1000000:
            representation['records'] = round(records/1000000, 2)
            representation["record_unit"] = 'M' 
        elif records > 1000:
            representation['records'] = round(records/1000, 2)
            representation["record_unit"] = 'k' 
        else:
            representation["record_unit"] = '' 
 
        return representation

class ThingsSensorsDataSerializer(serializers.ModelSerializer):
    dtread = serializers.DateTimeField(source='timestamp_period')  # Define um campo personalizado 'dtread' usando o alias 'timestamp_period'

    class Meta:
        model = ThingsSensorsDataModel
        fields = ('dtread',
                  'value',
                  'message',
       
        )

