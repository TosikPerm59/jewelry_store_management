import os.path

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse, response, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Jewelry, User, File, InputInvoice, OutgoingInvoice, Counterparties
from product_guide.services.invoice_parser import invoice_parsing, word_invoice_parsing
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.services.anover_functions import search_query_processing, \
    make_product_dict_from_dbqueryset, get_context_for_product_list, save_invoice, form_type_check, \
    make_product_dict_from_paginator, make_product_queryset_from_dict_dicts, filters_check, \
    get_outgoing_invoice_title_list, get_files_title_list
from django.contrib.auth.decorators import login_required
from product_guide.services.giis_parser import giis_file_parsing
from .services.outgoing_invoice_changer import change_outgoing_invoice
from .services.readers import read_excel_file, read_msword_file


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

    product_dicts_dict, counter, product_list = {}, 0, []
    user = request.user
    prod_name = prod_metal = prod_uin = prod_id = prod_art = prod_weight = None
    prod_name = request.POST.get('name') if request.POST.get('name') else 'all'
    prod_metal = request.POST.get('metal') if request.POST.get('metal') else 'all'
    availability_status = request.POST.get('availability_status')
    page_num = request.POST.get('page')
    search_string = request.POST.get('search_string')

    if search_string:
        prod_name, prod_metal, prod_uin, prod_id, prod_art, prod_weight = search_query_processing(search_string)

    if filters_check(prod_name, prod_metal) == 'all':
        if 'filtered_list' in request.session.keys() and page_num is None:
            request.session.pop('filtered_list')

    if request.method == 'POST':

        product_dicts_dict = request.session['product_objects_dict_for_view']

        product_list = make_product_queryset_from_dict_dicts(product_dicts_dict)
        if prod_name != 'all':
            product_list = [p for p in product_list if p['name'] == prod_name]
            request.session['filtered_list'] = make_product_dict_from_dbqueryset(product_list)
        if prod_metal != 'all':
            product_list = [p for p in product_list if p['metal'] == prod_metal] if prod_metal != 'all' else product_list
            request.session['filtered_list'] = make_product_dict_from_dbqueryset(product_list)
        product_dicts_dict = make_product_dict_from_dbqueryset(product_list)

    else:
        products_queryset = Jewelry.objects.all().values()
        # print(products_queryset)
        product_dicts_dict = make_product_dict_from_dbqueryset(products_queryset)

        request.session['product_objects_dict_for_view'] = product_dicts_dict
        request.session.save()

    if page_num:
        if 'filtered_list' in request.session.keys():
            product_dicts_dict = request.session['filtered_list']
            context = get_context_for_product_list(product_dicts_dict, page_num)
        else:
            context = get_context_for_product_list(product_dicts_dict, page_num)

    else:

        context = get_context_for_product_list(product_dicts_dict, page_num)
    # print(context['product_list'])
    return render(request, 'product_guide\product_base_v2.html', context=context)


@login_required()
def upload_file(request):
    products_dicts_dict = {}
    file_type = None

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        file_name = request.FILES['file'].name.replace(' ', '_') if ' ' in request.FILES['file'].name else \
            request.FILES['file'].name
        file_name = file_name.replace('№', '') if '№' in file_name else file_name
        file_type = 'excel' if file_name.endswith('.xls') or file_name.endswith('xlsx') else None
        if file_type is None:
            file_type = 'msword' if file_name.endswith('.doc') or file_name.endswith('docx') else None
        form.title = file_name

        if form.is_valid():
            duplicate_file = False
            files_queryset = File.objects.all()
            files_title_list = get_files_title_list(files_queryset)
            if file_name not in files_title_list:
                save_invoice(form, file_name)
            else:
                duplicate_file = True

            file_path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\' + file_name

            if file_type == 'excel':

                full_rows_list, sheet, file_type = read_excel_file(file_path)

                if form_type_check(full_rows_list, sheet, file_name) == 'giis_report':
                    products_dicts_dict = giis_file_parsing(full_rows_list, sheet)
                    invoice = {'giis_report': True}
                    request.session['invoice'] = invoice

                else:
                    products_dicts_dict, invoice_date, invoice_number, provider = invoice_parsing(full_rows_list, sheet, file_type, file_name)

                    invoice = {
                        'arrival_date': invoice_date,
                        'provider': provider,
                        'invoice_number': invoice_number,
                        'recipient': None,
                        'title': file_name
                    }
                    request.session['invoice'] = invoice

            elif file_type == 'msword':

                header_table, product_table = read_msword_file(file_path)
                products_dicts_dict, invoice_requisites = word_invoice_parsing(header_table, product_table)

                if invoice_requisites['provider_id'] == 1:

                    if file_name not in get_outgoing_invoice_title_list(OutgoingInvoice.objects.all()):
                        invoice_object = OutgoingInvoice()
                        invoice_object.departure_date = invoice_requisites['departure_date']
                        invoice_object.title = file_name
                        invoice_object.invoice_number = int(invoice_requisites['invoice_number'])
                        invoice_object.recipient_id = invoice_requisites['recipient_id']
                        invoice_object.save()

                if duplicate_file is False:
                    change_outgoing_invoice(file_path)

                context = get_context_for_product_list(products_dicts_dict, page_num=None)
                context['recipient'] = Counterparties.objects.get(id=invoice_requisites['recipient_id'])
                context['departure_date'] = invoice_requisites['departure_date']
                context['invoice_title'] = file_name.split('.')[0]
                context['file_path'] = file_path
                context['file_name'] = file_name
                request.session['product_objects_dict_for_view'] = products_dicts_dict
                request.session['outgoing_invoice'] = invoice_requisites

                return render(request, 'product_guide\outgoing_invoice_view.html', context=context)

    # print(products_dicts_dict)
    request.session['product_objects_dict_for_view'] = products_dicts_dict

    context = get_context_for_product_list(products_dicts_dict, page_num=None)
    # print(context['product_list'])
    return render(request, 'product_guide\product_base_v2.html', context=context)


@login_required()
def change_product_attr(request):
    product_number = int(request.POST.get('product.number'))
    product_objects_dict, product_list = None, None

    if request.method == 'POST':
        product_objects_dict = request.session['product_objects_dict_for_view']
        for product_key, product_value in product_objects_dict.items():
            if product_value['number'] == product_number:
                product_value['name'] = request.POST.get('product.name')
                product_value['metal'] = request.POST.get('product.metal')
                product_value['weight'] = request.POST.get('product.weight')
                product_value['vendor_code'] = request.POST.get('product.vendor_code')
                product_value['barcode'] = request.POST.get('product.barcode')
                product_value['uin'] = request.POST.get('product.uin')
                break

        request.session['product_objects_dict_for_view'] = product_objects_dict

    context = get_context_for_product_list(product_objects_dict, page_num=None)

    return render(request, 'product_guide\product_base_v2.html', context=context)


@login_required()
def delete_line(request):
    product_number = int(request.POST.get('product.number'))
    print('delete product_number = ', product_number)
    product_objects_dict, product_list = None, None

    if request.method == 'POST':
        product_objects_dict = request.session['product_objects_dict_for_view']

        for product_key, product_value in product_objects_dict.items():

            if product_value['number'] == product_number:
                product_objects_dict.pop(product_key)
                break

        request.session['product_objects_dict_for_view'] = product_objects_dict

    context = get_context_for_product_list(product_objects_dict, page_num=None)

    return render(request, 'product_guide\product_base_v2.html', context=context)


@login_required()
def save_products(request):
    invoice, invoice_object = None, None
    products_dbqueryset = Jewelry.objects.all().values()
    repeating_product = False
    product_dicts_dict_from_session = request.session['product_objects_dict_for_view']

    invoice_dict = request.session['invoice']

    if 'giis_report' not in invoice_dict:
        try:
            invoice_object = InputInvoice.objects.get(title=invoice_dict['title'])
        except ObjectDoesNotExist:
            invoice_object = InputInvoice(
                title=invoice_dict['title'],
                invoice_number=invoice_dict['invoice_number'],
                recipient=invoice_dict['recipient'],
                arrival_date=invoice_dict['arrival_date']
            )
            invoice_object.save()

    for product in product_dicts_dict_from_session.values():
        item_object = Jewelry()
        # print(item_object.__dict__)
        for key, value in product.items():

            if product[key] is not None and key != 'number':

                item_object.__setattr__(key, value)


        for product_from_dbqueryset in products_dbqueryset:

            invoice_id = product_from_dbqueryset['input_invoice_id']

            if (item_object.barcode == product_from_dbqueryset['barcode'] and item_object.barcode is not None or
                    item_object.uin == product_from_dbqueryset['uin'] and item_object.uin is not None or
                    (item_object.name == product_from_dbqueryset['name'] and item_object.metal ==
                     product_from_dbqueryset['metal'] and
                     item_object.weight == float(product_from_dbqueryset['weight']) and
                     item_object.vendor_code == product_from_dbqueryset['vendor_code'] and
                     item_object.input_invoice == InputInvoice.objects.get(id=invoice_id))
                ):
                repeating_product = True


        if repeating_product is False:

            item_object.save()
        else:
            repeating_product = False

    context = get_context_for_product_list(product_dicts_dict_from_session, page_num=None)

    return render(request, 'product_guide\product_base_v2.html', context=context)


def download_file(request):
    file_path = request.GET.get('file_path')
    file_name = request.GET.get('file_name')
    response = FileResponse(open(file_path, 'rb'))
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = 'attachment; filename='
    response['Content-Disposition'] += file_name
    return response


def save_availability_status_and_set_recipient_for_products(request):

    products_dicts_dict = request.session['product_objects_dict_for_view']
    invoice_requisites = request.session['outgoing_invoice']
    for product in products_dicts_dict.values():
        try:
            product_object = Jewelry.objects.get(uin=product['uin'])
            if product_object:
                product_object.availability_status = 'Передано'
                product_object.recipient_id = invoice_requisites['recipient_id']
                product_object.save()
        except ObjectDoesNotExist:
            pass

