from django.shortcuts import render, HttpResponse
from accounts.forms import NewUser

from django.contrib.auth import authenticate, login, logout
# Create your views here.
def index(request):
    form = NewUser(request.POST)

    if form.is_valid():
        form.save()
        msg = "Usuário cadastrado"
    else:
        msg = "Erro no cadastro"

    return HttpResponse(msg)

def signup(request):
    title = "Contas"
    form = NewUser()
    
    context = {'title_page': title,
               'form': form,
              }
    return render(request, "account.html", context)

def signin(request):
    if request.method == 'POST':
        user.authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            login(request, user)

    return render(request, "account-login.html", {})

def signout(request):
    logout(request)
    return HttpResponse('OK')

