from django.shortcuts import render, HttpResponse

# Create your views here.
def signup(request):
    return render(request, "account.html", {})

