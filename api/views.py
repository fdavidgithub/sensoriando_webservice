from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

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
    queryset  = AccountsModel.objects.filter(status = True, id_plan__ispublic = True)

class PrivateAccountViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset  = AccountsModel.objects.filter(status = True, id_plan__ispublic = False)

class PublicThingsViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.DataThingsSerializer
    queryset = AccountsThingsModel.objects.filter(id_account__status = True, id_account__id_plan__ispublic = True)

