from django.shortcuts import render, HttpResponse, redirect
from base.forms import category_form
from base.models import Category
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
@staff_member_required
def category(request):
    context = {'title_page': "Categorias",
               'form': category_form(request.POST),
               'categories': Category.objects.all(),
    }

    return render(request, "base-category.html", context)

def new(request):
    form = category_form(request.POST)

    if form.is_valid():
        form.save()

    return redirect('category')

