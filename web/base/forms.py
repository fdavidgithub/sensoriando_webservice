from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .legacy_tables import Accounts, Accountsthings

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    email = forms.EmailField(max_length=254, required=True, help_text='Obrigatório, informe um endereço de e-mail válido.')

    city = forms.CharField(max_length=50, required=True, help_text='Obrigatório.')
    state = forms.CharField(max_length=2, required=True, help_text='Obrigatório.')
    country = forms.CharField(max_length=20, required=True, help_text='Obrigatório.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'city', 'state', 'country', )

class AccountForm(ModelForm):
    class Meta:
        model = Accounts
        fields = ('city', 'state', 'country', )

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email' )

class ThingForm(ModelForm):
    uuid = forms.UUIDField(required=True, help_text='Obrigatório.')
 
    class Meta:
        model = Accountsthings
        fields = ('uuid',)

