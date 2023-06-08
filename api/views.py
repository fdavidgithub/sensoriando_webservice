from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.db.models import Q

from api import serializers
from base.models import ThingsModel, ThingsTagsModel, SensorsModel, ThingsSensorsTagsModel, AccountsModel, \
                        ThingsSensorsModel, AccountsThingsModel

class ThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingSerializer
    queryset  = ThingsModel.objects.all()

class ThingTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingTagSerializer
    queryset  = ThingsTagsModel.objects.values('name').distinct()

class SensorViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorSerializer
    queryset  = SensorsModel.objects.all()

class SensorTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorTagSerializer
    queryset  = ThingsSensorsTagsModel.objects.values('name').distinct()

class PublicAccountViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset  = AccountsModel.objects.filter(
        status = True, 
        id_plan__ispublic = True,
    )

class PrivateAccountViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset  = AccountsModel.objects.filter(
        status = True, 
        id_plan__ispublic = False,
    )

class PublicThingsViewSets(APIView):
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.GET)
        serializer = serializers.DataThingsSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'thing': openapi.Schema(type=openapi.TYPE_STRING),
                'city': openapi.Schema(type=openapi.TYPE_STRING),
                'state': openapi.Schema(type=openapi.TYPE_STRING),
                'country': openapi.Schema(type=openapi.TYPE_STRING),
                'sensor': openapi.Schema(type=openapi.TYPE_STRING),
                'thing_tag': openapi.Schema(type=openapi.TYPE_STRING),
                'sensor_tag': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.POST)

        """
        for key, value in request.data.items():
            if key == "thing":
                queryset = queryset.filter(id_thing__name = value)
            elif key == "city":
                queryset = queryset.filter(id_account__city = value)
            elif key == "state":
                queryset = queryset.filter(id_account__state = value)
            elif key == "country":
                queryset = queryset.filter(id_account__country = value)
            elif key == "sensor":
                #thingssensors = ThingsSensorsModel.objects.filter(id_sensor__name = value)
                #thing_ids = [ts.id_thing_id for ts in thingssensors]
                thing_ids = ThingsSensorsModel.objects.filter(id_sensor__name = value).values_list("id_thing_id", flat=True)
                
                queryset = queryset.filter(id_thing__in = thing_ids)
            elif key == "tag":
                #thingstags = ThingsTagsModel.objects.filter(name = value)
                #thing_ids = [ts.id_thing_id for ts in thingstags]
                thing_ids = ThingsTagsModel.objects.filter(name = value).values_list("id_thing_id", flat=True)
                
                queryset = queryset.filter(id_thing__in = thing_ids)
        """

        q_objects = []
        filters = {
            "thing": lambda value: Q(id_thing__name = value),
            "city": lambda value: Q(id_account__city = value),
            "state": lambda value: Q(id_account__state = value),
            "country": lambda value: Q(id_account__country = value),
            "sensor": lambda value: Q(id_thing__in = self.filter_things_sensors(value)),
            "thing_tag": lambda value: Q(id_thing__in = self.filter_things_tags(value)),
            "sensor_tag": lambda value: Q(id_thing__in = self.filter_sensors_tags(value)),
        }

        for key, value in request.data.items():
            filter_func = filters.get(key)
            if filter_func:
                q_objects.append(filter_func(value))
        
        if q_objects:
            queryset = queryset.filter(*q_objects)

        serializer = serializers.DataThingsSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, params):
        return AccountsThingsModel.objects.filter(
            id_account__status = True, 
            id_account__id_plan__ispublic = True,
        )
   
    def filter_things_sensors(self, value):
        thing_ids = ThingsSensorsModel.objects.filter(id_sensor__name = value).values_list("id_thing_id", flat = True)
        return thing_ids

    def filter_things_tags(self, value):
        thing_ids = ThingsTagsModel.objects.filter(name = value).values_list("id_thing_id", flat = True)
        return thing_ids
 
    def filter_sensors_tags(self, value):
        thingsensor_ids = ThingsSensorsTagsModel.objects.filter(name = value).values_list("id_thingsensor_id", flat = True)
        thing_ids = ThingsSensorsModel.objects.filter(id__in = thingsensor_ids).values_list("id_thing", flat = True)
        return thing_ids
 