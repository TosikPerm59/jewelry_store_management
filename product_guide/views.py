import os.path
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
import xlrd
import datetime
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from unicodedata import decimal

from .models import Jewelry, User, File, InputInvoice
from product_guide.services.invoice_parser import invoice_parsing
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.services.anover_functions import search_query_processing
from django.contrib.auth.decorators import login_required


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


def upload_file(request):

    provider, invoice_date, invoice_number = None, None, None
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file_name = request.FILES['file'].name.replace(' ', '_') if ' ' in request.FILES['file'].name else request.FILES['file'].name
        file_type = 'excel' if file_name.endswith('.xls') or file_name.endswith('xlsx') else 'word'
        form.title = file_name

        if form.is_valid():

            file_title_list = []
            product_dicts_dict = []
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
                product_dicts_dict, invoice_date, invoice_number, provider = invoice_parsing(file_path)

            invoice = {
                'arrival_date': datetime.datetime.strptime(invoice_date, "%d.%m.%Y").strftime("%Y-%m-%d"),
                'provider': provider,
                'invoice_number': invoice_number,
                'recipient': None,
                'title': file_name
            }

            request.session['product_objects_list'] = product_dicts_dict
            print(request.session.items())
            request.session['invoice'] = invoice
            request.session['data_for_view'] = product_dicts_dict
            return render(request, 'product_guide\product_base_v2.html', {'product_list': product_dicts_dict})
    return render(request, 'product_guide/index.html')


def change_product_attr(request):
    product_number = request.POST.get('product.number')
    product_objects_list = None

    if request.method == 'POST':

        product_objects_list = request.session['product_objects_list']
        variable_product = product_objects_list[product_number]

        variable_product['name'] = request.POST.get('product.name')
        variable_product['metal'] = request.POST.get('product.metal')
        variable_product['weight'] = request.POST.get('product.weight')
        variable_product['art'] = request.POST.get('product.art')
        variable_product['barcode'] = request.POST.get('product.barcode')
        variable_product['uin'] = request.POST.get('product.uin')

        product_objects_list[product_number] = variable_product
        request.session['product_objects_list'] = product_objects_list

    return render(request, 'product_guide\product_base_v2.html', {'product_list': product_objects_list})


def delete_line(request):
    product_number = request.POST.get('product.number')
    product_objects_list = None
    if request.method == 'POST':

        product_objects_list = request.session['product_objects_list']
        product_objects_list.pop(product_number)
        request.session['product_objects_list'] = product_objects_list

    return render(request, 'product_guide\product_base_v2.html', {'product_list': product_objects_list})


def save_products(request):
    invoice, input_invoice = None, None
    product_objects_list = Jewelry.objects.all().values()
    repeating_product = False
    product_objects_dict = request.session['product_objects_list']

    invoice_dict = request.session['invoice']

    try:
        invoice_object = InputInvoice.objects.get(title=invoice_dict['title'])
    except ObjectDoesNotExist:
        invoice_object = InputInvoice(
            title=invoice_dict['title'],
            provider=invoice_dict['provider'],
            invoice_number=invoice_dict['invoice_number'],
            recipient=invoice_dict['recipient'],
            arrival_date=invoice_dict['arrival_date']
        )
        invoice_object.save()

    for product in product_objects_dict.values():

        item_object = Jewelry(
            name=product['name'],
            metal=product['metal'],
            weight=product['weight'],
            vendor_code=product['art'],
            barcode=product['barcode'],
            uin=product['uin'],
            provider=invoice_dict['provider'],
            arrival_date=invoice_dict['arrival_date'],
            input_invoice=invoice_object
        )
        for product_from_base in product_objects_list:
            print(product_from_base)
            try:
                input_invoice = InputInvoice.objects.get(id=product_from_base['id'])['title']
            except ObjectDoesNotExist:
                pass

            if (item_object.barcode == product_from_base['barcode'] or
                item_object.uin == product_from_base['uin'] or
                (item_object.name == product_from_base['name'] and item_object.metal == product_from_base['metal'] and
                    item_object.weight == float(product_from_base['weight']) and
                    item_object.vendor_code == product_from_base['vendor_code'] and
                    item_object.input_invoice == input_invoice)
                    ):
                repeating_product = True

        if repeating_product is False:
            item_object.save()
        else:
            repeating_product = False

    return render(request, 'product_guide\product_base_v2.html', {'product_list': product_objects_dict})