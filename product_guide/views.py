from django.shortcuts import render
from django.http import HttpResponse
from .models import Jewelry


def index(request):
    return render(request, 'product_guide\index.html')


def product_base(request):
    name = request.GET.get('name')
    metal = request.GET.get('metal')
    search = request.GET.get('search_string')
    availability_status = request.GET.get('availability_status')
    product_list = Jewelry.objects.all()
    if 'all' != name is not None:
        product_list = product_list.filter(name=name)
    if 'all' != metal is not None:
        product_list = product_list.filter(metal=metal)
    if 'all' != availability_status is not None:
        product_list = product_list.filter(availability_status=availability_status)
    context = {
        'product_list': product_list,
        'product_name_filter': name,
        'product_metal_filter': metal
    }
    return render(request, 'product_guide\product_base_v2.html', context)



