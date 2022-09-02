from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.http import HttpResponse
from .models import Jewelry
from .anover_functions import search_query_processing


def register(request):
    return HttpResponse('Вы находитесь на странице регистрации')


def login(request):
    return HttpResponse('Вход')


def index(request):
    return render(request, 'product_guide\index.html')


def product_base(request):
    prod_name = prod_metal = prod_uin = prod_id = prod_art = prod_weight = None
    prod_name = request.GET.get('name')
    prod_metal = request.GET.get('metal')
    search_string = request.GET.get('search_string')
    if search_string:
        prod_name, prod_metal, prod_uin, prod_id, prod_art, prod_weight = search_query_processing(search_string)
    availability_status = request.GET.get('availability_status')
    product_list = Jewelry.objects.all()
    if 'all' != prod_name is not None:
        product_list = product_list.filter(name=prod_name)
    if 'all' != prod_metal is not None:
        product_list = product_list.filter(metal=prod_metal)
    if 'all' != availability_status is not None:
        product_list = product_list.filter(availability_status=availability_status)
    if 'all' != prod_uin is not None:
        product_list = product_list.filter(uin=prod_uin)
    context = {
        'product_list': product_list,
        'product_name_filter': prod_name,
        'product_metal_filter': prod_metal
    }
    return render(request, 'product_guide\product_base_v2.html', context)



