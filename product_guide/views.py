import os.path

import xlrd
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.template.context_processors import media

from .models import Jewelry, User, File
from product_guide.services.invoice_parser import invoice_parsing
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.services.anover_functions import search_query_processing
from django.contrib.auth.decorators import login_required
from product_guide.services.readers import read_excel_file


def register(request):
    context = {'number_of_messages': 0}
    user_names = User.objects.all().values('username')
    users = User.objects.all().values()
    username_list, message = [], []
    for user in user_names:
        username_list.append(user['username'])
    if request.method == 'POST':
        condition = True
        user_name = request.POST.get('name')
        user_surname = request.POST.get('surname')
        user_email = request.POST.get('email')
        user_nick_name = user_name + '_' + user_surname
        user_password_1 = request.POST.get('password_1')
        user_password_2 = request.POST.get('password_2')

        context = {
            'name': user_name,
            'surname': user_surname,
            'email': user_email,
            'password_1': user_password_1,
            'password_2': user_password_2
        }

        if user_nick_name in username_list:
            message.append('Такой пользователь уже существует!')
            condition = False
        if user_password_1 != user_password_2:
            message.append('Пароли отличаются!')
            condition = False
        if len(message) > 0:
            context['messages'] = message
            context['number_of_messages'] = len(message)

        if condition:
            user = User.objects.create_user(
                user_nick_name,
                user_email,
                user_password_1
            )
            user.first_name = user_name
            user.last_name = user_surname
            user.save()
            login(request, user)

            return render(request, 'product_guide\index.html')

    return render(request, 'product_guide/register.html', context=context)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('login_input')
        password = request.POST.get('password_input')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect('product_guide/index.html')

    return render(request, 'product_guide/login.html')


def user_logout(request):
    logout(request)
    return redirect('index')


def index(request):
    form = UploadFileForm
    return render(request, 'product_guide\index.html', {'form': form})


@login_required()
def product_base(request):
    user = request.user
    print(user)
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
        'current_name': prod_name,
        'current_metal': prod_metal
    }
    return render(request, 'product_guide\product_base_v2.html', context=context)


def handle_uploaded_file(f):
    with open('some/file/name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file_name = request.FILES['file'].name.replace(' ', '_') if ' ' in request.FILES['file'].name else request.FILES['file'].name
        file_type = 'excel' if file_name.endswith('.xls') or file_name.endswith('xlsx') else 'word'
        form.title = file_name

        if form.is_valid():
            file_title_list = []
            product_objects_list = []
            print('FORM VALID')
            for file_object in File.objects.all():
                file_title_list.append(file_object.title)
            if file_name not in file_title_list:
                form.save()
                file_object = File.objects.latest('id')
                file_object.title = file_name
                file_object.save()
            file_path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\' + file_name
            if file_type == 'excel':
                product_objects_list = invoice_parsing(file_path)
            return render(request, 'product_guide\product_base_v2.html', {'product_list': product_objects_list})
    return render(request, 'product_guide/index.html')
