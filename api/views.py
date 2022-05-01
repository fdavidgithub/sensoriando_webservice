from rest_framework import viewsets
from . import serializers
from . import models

class ThingViewSets(viewsets.ModelViewSet):
    serializer_class = serializers.ThingSerializer
    queryset  = models.Things.objects.all()

