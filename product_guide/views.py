from django.shortcuts import render
from django.http import HttpResponse
from .models import Jewelry


def index(request):
    return render(request, 'product_guide\index.html')


def product_base(request):
    product_list = Jewelry.objects.all
    context = {'product_list': product_list}

    return render(request, 'product_guide\product_base.html', context)
