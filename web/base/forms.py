from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import ugettext_lazy as _

from .legacy_tables import Accounts, Accountsthings, Things
from .constants import COUNTRY_CHOICES, BRAZIL_STATES_CHOICES

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    email = forms.EmailField(max_length=254, required=True, help_text='Obrigatório que seja um endereço de e-mail válido.')

    city = forms.CharField(max_length=50, required=True, help_text='Obrigatório.', label='Cidade')
    state = forms.CharField(max_length=2, required=True, help_text='Obrigatório.', label='Estado', widget=forms.Select(choices=BRAZIL_STATES_CHOICES))
    country = forms.CharField(max_length=20, required=True, help_text='Obrigatório.', label='País', widget=forms.Select(choices=COUNTRY_CHOICES))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'city', 'state', 'country', )

class AccountForm(ModelForm):
    city = forms.CharField(max_length=50, required=True, help_text='Obrigatório.', label='Cidade')
    state = forms.CharField(max_length=2, required=True, help_text='Obrigatório.', label='Estado', widget=forms.Select(choices=BRAZIL_STATES_CHOICES))
    country = forms.CharField(max_length=20, required=True, help_text='Obrigatório.', label='País', widget=forms.Select(choices=COUNTRY_CHOICES))
    
    class Meta:
        model = Accounts
        fields = ('city', 'state', 'country', )

class UserForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Obrigatório.')
    email = forms.EmailField(max_length=254, required=True, help_text='Obrigatório que seja um endereço de e-mail válido.')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email' )

class ThingForm(ModelForm):
    uuid = forms.UUIDField(required=True, help_text='Digite o UUID, obrigatório.', label='Nova central')

    def clean_uuid(self):
        uuid = self.cleaned_data.get('uuid')
        
        try:
            thing = Things.objects.get(uuid = uuid)
        except ObjectDoesNotExist:
            raise ValidationError(_('UUID não encontrado'))
     
        try:
            Accountsthings.objects.get(id_thing = thing.id)
            raise ValidationError(_('UUID indisponível'))
        except ObjectDoesNotExist:
            pass
        
        return uuid

    class Meta:
        model = Accountsthings
        fields = ('uuid',)

