from django.urls import path, include
from django.contrib.auth import views as auth_views

from users import views

app_name = 'users'

#https://learndjango.com/tutorials/django-login-and-logout-tutorial
urlpatterns = [
    path('signup/', views.SignUp, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', views.SignIn.as_view(), name='login'),
    path('account/<str:username>/<str:tab>', views.MyAccount, name='account'),
]

