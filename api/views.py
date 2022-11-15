from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from api import serializers
from api import models

class ThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingSerializer
    queryset  = models.Things.objects.all()

class ThingTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingTagSerializer
    queryset  = models.Thingstags.objects.all()

class SensorViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorSerializer
    queryset  = models.Sensors.objects.all()

class SensorTagViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.SensorTagSerializer
    queryset  = models.Thingssensorstags.objects.all()

class PublicAccountViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset  = models.Accounts.objects.filter(status = True, id_plan__ispublic = True)

class PrivateAccountViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountSerializer
    queryset  = models.Accounts.objects.filter(status = True, id_plan__ispublic = False)

class AccountThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.AccountThingSerializer
    queryset  = models.Accountsthings.objects \
        .select_related('id_thing') \
        .filter(id_account = 1)

class AccountThingSensorTagView(APIView):
    serializer_class = serializers.AccountThingSensorTagSerializer

    def get_queryset(self):
        accounts = models.Accountsthings.objects.all()
        return accounts

    def get(self, requests):
        accounts = self.get_queryset()
        serializer = serializers.AccountThingSensorTagSerializer(accounts, many=True)

        return Response(serializer.data)
