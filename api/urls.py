from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'thing', views.ThingViewSets, basename='thing')
router.register(r'sensor', views.SensorViewSets, basename='sensor')
router.register(r'tag', views.TagViewSets, basename='tag')


urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]


