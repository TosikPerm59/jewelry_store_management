from django.shortcuts import render
from django.http import HttpResponse
from .models import Jewelry


def index(request):
    return render(request, 'product_guide\index.html')


def product_base(request):
    name = request.GET.get('name')
    metal = request.GET.get('metal')
    if name == metal == 'all' or name == metal is None:
        product_list = Jewelry.objects.all
    else:
        product_list = Jewelry.objects.filter(name=name, metal=metal)
    context = {
        'product_list': product_list,
        'product_name_filter': name,
        'product_metal_filter': metal
    }
    return render(request, 'product_guide\product_base_v2.html', context)



