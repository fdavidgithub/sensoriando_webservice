from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncSecond, TruncMinute, TruncHour, TruncDay, TruncMonth, TruncYear
from django.db.models import Avg, F

from api import serializers
from base.models import ThingsModel, ThingsTagsModel, SensorsModel, ThingsSensorsTagsModel, AccountsModel, \
                        ThingsSensorsModel, AccountsThingsModel, ThingsSensorsDataModel, PlansModel

class ThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingSerializer
    queryset  = ThingsModel.objects.all()

class ThingTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingTagSerializer
    queryset  = ThingsTagsModel.objects.values('name').distinct()

class SensorViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorSerializer
    queryset  = SensorsModel.objects.all()

class PublicSensorTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorTagSerializer
    thingPublic_ids = AccountsThingsModel.objects.filter(id_account__id_plan__ispublic = True).values('id_thing_id')
    queryset  = ThingsSensorsTagsModel.objects.filter(id_thingsensor__id_thing__in = thingPublic_ids).values('name').distinct()

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
#    def get(self, request, *args, **kwargs):
#        queryset = self.get_queryset(request.GET)
#        serializer = serializers.DataThingsSerializer(queryset, many=True)
#        return Response(serializer.data)

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

class DataViewSets(APIView):
    isPublic = None

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'thing': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                'sensor': openapi.Schema(type=openapi.TYPE_STRING),
                'period': openapi.Schema(type=openapi.TYPE_STRING, default="second", description="Permitted values: second, minute, hour, day, month, year"),
            
            }
        )
    )
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        serializer = serializers.ThingsSensorsDataSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, request):
        data = None
        lastread = None

        try:
            thing = request.data["thing"]
        except:
            thing = None
            
        try:
            sensor = request.data["sensor"]
        except:
            sensor = None

        try:
            period = request.data["period"].lower()
        except:
            period = 'second'

        period_mapping = {
            "second": TruncSecond,
            "minute": TruncMinute,
            "hour": TruncHour,
            "day": TruncDay,
            "month": TruncMonth,
            "year": TruncYear,
        }

        checkPublic = AccountsThingsModel.objects.filter(
            id_thing__uuid = thing,
            id_account__id_plan__ispublic = self.isPublic,
        )

        if checkPublic:
            lastread = ThingsSensorsDataModel.objects.filter(
                id_thingsensor__id_thing__uuid = thing,
                id_thingsensor__id_sensor__name = sensor,

            ).last()

        if lastread and period in period_mapping:
            trunc_class = period_mapping[period]
            dt_lastread = lastread.dtread.astimezone()

            if period == "second":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,

                    dtread__year = dt_lastread.year,
                    dtread__month = dt_lastread.month,
                    dtread__day = dt_lastread.day,
                    dtread__hour = dt_lastread.hour,
                    dtread__minute = dt_lastread.minute,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )
            elif period == "minute":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,

                    dtread__year = dt_lastread.year,
                    dtread__month = dt_lastread.month,
                    dtread__day = dt_lastread.day,
                    dtread__hour = dt_lastread.hour,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )
            elif period == "hour":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,

                    dtread__year = dt_lastread.year,
                    dtread__month = dt_lastread.month,
                    dtread__day = dt_lastread.day,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )
            elif period == "day":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,

                    dtread__year = dt_lastread.year,
                    dtread__month = dt_lastread.month,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )
            elif period == "month":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,

                    dtread__year = dt_lastread.year,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )
            elif period == "year":
                data = ThingsSensorsDataModel.objects.filter(
                    id_thingsensor__id_thing__uuid = thing,
                    id_thingsensor__id_sensor__name = sensor,
                ).annotate(
                    timestamp_period = trunc_class('dtread')  # Truncate dtread to the nearest second
                ).values(
                    'timestamp_period'  # Group by truncated dtread
                ).annotate(
                    value = Avg('value')  # Calculate average value per second
                ).order_by(
                    'timestamp_period'  # Order by dtread ascending
                )

        return data
   
class PublicDetailViewSets(DataViewSets):
    isPublic = True

#Abourt token
#https://django-rest-framework-simplejwt.readthedocs.io/en/latest/getting_started.html
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PrivateDetailViewSets(DataViewSets):
    isPublic = False

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PrivateThingsViewSets(APIView):
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
        queryset = self.get_queryset(params = request.POST, user = request.user)

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

    def get_queryset(self, params, user):
        Account = AccountsModel.objects.get(username = user)
        account_id = Account.id
        
        return AccountsThingsModel.objects.filter(
            id_account__status = True, 
            id_account__id_plan__ispublic = False,
            id_account = account_id,

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

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class PrivateStatisticsViewSets(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        id_account = AccountsModel.objects.get(username = user).id

        data = {
            'user': user,
            'plan': self.get_plan(id_account),
            'records': self.get_records(id_account),
            'retation_full': self.get_retation_plan(id_account),
            'retation_unit': None,
            'retation_current': None,
            'record_unit': None,

        }

        serializer = serializers.DataStatsSerializer(data)
        return Response(serializer.data)

    def get_records(self, id_account):
        thing_ids = AccountsThingsModel.objects.filter(
            id_account = id_account

        ).values_list("id_thing", flat = True)
       
        thingsensor_ids = ThingsSensorsModel.objects.filter(
            id_thing__in = thing_ids,

        ).values_list("id", flat = True)
 
        return ThingsSensorsDataModel.objects.filter(
            id_thingsensor__in = thingsensor_ids,

        ).count()
     
    def get_plan(self, id_account):
        account = AccountsModel.objects.get(id = id_account)

        return account.id_plan.name
      
    def get_retation_plan(self, id_account):
        account = AccountsModel.objects.get(id = id_account)

        return account.id_plan.retation

