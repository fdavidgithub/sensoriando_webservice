from django.urls import path, include

from rest_framework import routers, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from api import views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Sensoriando API",
      default_version='beta',
      description="-= description =-",
      #terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="noBots@sensoriando.com.br"),
      license=openapi.License(name="copyright Sensoriando@2023"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

#router = routers.DefaultRouter()

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   
    path('data/public/thing/', views.PublicThingsViewSets.as_view({'get': 'list'}), name='PublicThings'),

    path('account/public/', views.PublicAccountViewSets.as_view({'get': 'list'}), name='PublicAccount'),
    path('account/private/', views.PrivateAccountViewSets.as_view({'get': 'list'}), name='PrivateAccount'),
    #path('account/thing/', views.AccountThingViewSets.as_view({'get': 'list'}), name='ThingsAccount'),
    #path('account/thing/tag/', views.AccountThingSensorTagView.as_view(), name='TagThingAccount'),
    
    path('thing/', views.ThingViewSets.as_view({'get': 'list'}), name='ListThings'),
    path('thing/tag/', views.ThingTagViewSets.as_view({'get': 'list'}), name='TagsThings'),

    path('sensor/', views.SensorViewSets.as_view({'get': 'list'}), name='ListSensors'),
    path('sensor/tag/', views.SensorTagViewSets.as_view({'get': 'list'}), name='TagsSensors'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]


