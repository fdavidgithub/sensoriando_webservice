from accounts.models import Account
from django.contrib.auth.forms import UserCreationForm

class NewUser(UserCreationForm):
    class Meta:
        model = Account
        fields = ['username',
                  'first_name',
                  'last_name',
                  'email',
                  'is_public',
                  'city',
                  'uf',
                ]
