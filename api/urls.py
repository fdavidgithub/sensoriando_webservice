from django.urls import path, include
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'thing', views.ThingViewSets, basename='thing')
router.register(r'sensor', views.SensorViewSets, basename='sensor')
router.register(r'thingtag', views.ThingTagViewSets, basename='thingtag')
router.register(r'sensortag', views.SensorTagViewSets, basename='sensortag')
router.register(r'publicaccount', views.PublicAccountViewSets, basename='publicaccount')
router.register(r'accountthing', views.AccountThingViewSets, basename='accountthing')


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accountthingtag', views.AccountThingSensorTagView.as_view())
]


