import os.path
import shutil
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .models import Jewelry, InputInvoice, Manufacturer
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.services.anover_functions import create_nomenclature_file
from django.contrib.auth.decorators import login_required
from .services.outgoing_invoice_changer import change_outgoing_invoice
from .services.testing_classes import Testing
import traceback
from .services.validity import check_id, check_uin
from .services.view_classes import createRequestObject


def show_exception(request, exception_text):

    splitted_exception_text = exception_text.split('\n')
    context = {'exception_list': splitted_exception_text}
    return render(request, 'product_guide/show_exception.html', context=context)


def register(request):
    context = {'number_of_messages': 0}
    user_names = User.objects.all().values('username')
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
    return render(request, 'product_guide/index.html', {'form': form})


@login_required()
def show_products(request):
    """ Представление, которое формирует список изделий для отображения. Формируется в зависимости от запроса.
            При GET запросе, отображаются все изделия хранящиеся в базе. При POST запросе, отображаются изделия
            в соответствии с запросом. POST запрос может быть с указанием номера страницы, с запросом поисковой
            строки или с запросом фильтрации данных. """

    try:
        request_obj = createRequestObject(request, 'ShowProducts')
        # Testing.show_session_data(request)
        print(len(Jewelry.objects.all()))
        return render(request, 'product_guide/product_base_v2.html', context=request_obj.context)

    except Exception:
        print('EXCEPTION')
        print(traceback.format_exc())
        return show_exception(request, traceback.format_exc())


@login_required()
def upload_file(request):
    """ Представление, которое обрабатывает загружаемый файл, формирует данные и загружает шаблон, в зависимости от типа
        загружаемого файла. """
    try:
        request_obj = createRequestObject(request, 'UploadFile')
        # Testing.show_session_data(request, show_products=False, show_invoice=True)
        # Testing.show_context_data(request_obj.context, show_lists=True)
        request.session.save()
        print('RENDERING')
        return render(request, request_obj.template_path, context=request_obj.context)

    except Exception:
        print('EXCEPTION')
        print(traceback.format_exc())
        return show_exception(request, traceback.format_exc())


@login_required()
def save_products(request):
    print('Сохранение изделий в базе данных')
    print('request.session.__dir__() = ', request.session._session_cache)
    products_queryset_from_bd = Jewelry.get_all_values()
    # print(request.session['products_objects_dict_for_view'])
    repeating_product = False
    product_dict_dicts_from_session = request.session['products_objects_dict_for_view']
    # print('product_dict_dicts_from_session = ', product_dict_dicts_from_session)
    invoice_requisites_from_session = request.session['invoice_requisites']
    previous_barcode, repeating_counter = None, 0
    uins_list_from_db = Jewelry.get_all_values_list('uin')
    print('len(uins_list_from_db) = ', len(uins_list_from_db))
    # print('uins_list_from_db = ', uins_list_from_db)
    barcodes_list_from_db = Jewelry.get_all_values_list('barcode')
    counter = 0
    if invoice_requisites_from_session['invoice_type'] != 'giis_report':
        invoice_object = InputInvoice.get_object('title', invoice_requisites_from_session['title'])

        if invoice_object is None:
            invoice_object = InputInvoice(
                title=invoice_requisites_from_session['title'],
                invoice_number=invoice_requisites_from_session['invoice_number'],
                recipient=invoice_requisites_from_session['recipient_id'],
                arrival_date=invoice_requisites_from_session['arrival_date']
            )
            invoice_object.save()

    for product_from_sessions_key, product_from_sessions_dict in product_dict_dicts_from_session.items():
        barcode_from_session_product = product_from_sessions_dict['barcode']
        if barcode_from_session_product is not None or barcode_from_session_product != 'None':
            if check_id(barcode_from_session_product):
                if int(barcode_from_session_product) in barcodes_list_from_db:
                    prod_obj = Jewelry.get_object('barcode', int(barcode_from_session_product))
                    if prod_obj.uin is None or prod_obj.uin == 'None':
                        prod_obj.uin = product_from_sessions_dict['uin']
                        prod_obj.save()
                    repeating_product = True
                else:
                    barcodes_list_from_db.append(int(product_from_sessions_dict['barcode']))
        if check_uin(product_from_sessions_dict['uin']):
            if int(product_from_sessions_dict['uin']) in uins_list_from_db:
                repeating_product = True
            else:
                uins_list_from_db.append(int(product_from_sessions_dict['uin']))

        if repeating_product is False:
            new_object = Jewelry()
            print(product_from_sessions_dict.items())
            for key, value in product_from_sessions_dict.items():
                if product_from_sessions_dict[key] is not None and key != 'number':
                    if key != 'manufacturer_id':
                        new_object.__setattr__(key, value)
                    else:
                        manufacturer_obj = Manufacturer.get_object('id', product_from_sessions_dict[key])
                        new_object.__setattr__('manufacturer', manufacturer_obj)
            print('New object = ', new_object.__dict__)
            try:
                new_object.save()
            except:
                print('EXCEPTION new_object_save')
                pass
        repeating_product = False

    context = get_context_for_product_list(product_dict_dicts_from_session, page_num=None)

    return render(request, 'product_guide/product_base_v2.html', context=context)


@login_required()
def save_incoming_invoice(request):
    pass
#     attr_list = ['name', 'metal', 'vendor_code', 'barcode', 'uin', 'weight', 'size', 'price']
#     product_dict = {}
#     # product_dict_dicts_from_session = RequestSession.get_product_dicts_dict_from_session(request)
#     product_dict_dicts = {}
#     # invoice_data = RequestSession.get_invoice_from_session(request)
#
#     provider_obj = get_or_save_provider(invoice_data)
#
#     input_invoice_obj = get_or_save_input_invoice_obj(invoice_data, provider_obj)
#
#     for number, product in product_dict_dicts_from_session.items():
#         print(number, product)
#         prod_obj = None
#         for attr in attr_list:
#             product_dict[attr] = request.POST.get(str(number) + '.' + attr)
#             # print('product_dict[attr] = ', product_dict[attr])
#         if product['uin'] != 'None' and product['uin'] is not None:
#             # print(product['uin'])
#             prod_obj = Jewelry.get_object('uin', product_dict['uin'])
#             if prod_obj:
#                 for attr in attr_list:
#
#                     if product_dict[attr] is not None and product_dict[attr] != 'None' and attr != 'uin':
#                         print(attr)
#                         value = product_dict[attr]
#                         if isinstance(value, str):
#                             value = value.replace(',', '.') if ',' in value else value
#                         setattr(prod_obj, attr, value)
#
#                 prod_obj.arrival_date = invoice_data['arrival_date']
#                 prod_obj.input_invoice_id = input_invoice_obj.id
#                 prod_obj.provider_id = provider_obj.id
#                 print(prod_obj.__dict__)
#                 prod_obj.save()
#                 if '_state' in prod_obj.__dict__:
#                     delattr(prod_obj, '_state')
#                     prod_obj.number = number
#
#         product_dict_dicts[number] = prod_obj.__dict__
#     request.session['product_objects_dict_for_view'] = product_dict_dicts
#     context = get_context_for_product_list(product_dict_dicts, page_num=None)
#     return render(request, 'product_guide/product_base_v2.html', context=context)


def download_nomenclature(request):
    file_path = request.GET.get('file_path')
    product_dict_dicts = request.session['product_objects_dict_for_view']
    invoice_dict = request.session['invoice']
    number = invoice_dict['invoice_number']
    file_nomenclature_path = create_nomenclature_file(file_path, product_dict_dicts, invoice_dict)
    response = FileResponse(open(file_nomenclature_path, 'rb'))
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = f'attachment; filename={number}.xlsx'

    return response


@login_required()
def download_changed_file(request):
    # async def delete_file(copy_path):
    #     await asyncio.sleep(100)
    #     os.remove(copy_path)
    #     return HttpResponse('Скачивание выполнено успешно')

    file_path = request.GET.get('file_path')
    print('file_path = ', file_path)
    path = os.path.split(file_path)[0] + '/media/'
    name = os.path.split(file_path)[1]
    copy_path = path + 'Копия' + name
    shutil.copyfile(file_path, copy_path)
    change_outgoing_invoice(copy_path)
    response = FileResponse(open(copy_path, 'rb'))
    response['content_type'] = "application/octet-stream"
    response['Content-Disposition'] = 'attachment; filename='

    # asyncio.run(delete_file(copy_path))
    return response


@login_required()
def change_product_attr(request):
    product_number = int(request.POST.get('product.number'))
    product_dict_dicts, product_list = None, None

    if request.method == 'POST':
        product_dict_dicts = request.session['product_objects_dict_for_view']
        for product_key, product_value in product_dict_dicts.items():
            if product_value['number'] == product_number:
                product_value['name'] = request.POST.get('product.name')
                product_value['metal'] = request.POST.get('product.metal')
                product_value['weight'] = request.POST.get('product.weight')
                product_value['vendor_code'] = request.POST.get('product.vendor_code')
                product_value['barcode'] = request.POST.get('product.barcode')
                product_value['uin'] = request.POST.get('product.uin')
                break

        # RequestSession.save_product_dicts_dict_in_session(request, product_dict_dicts)

    context = get_context_for_product_list(product_dict_dicts, page_num=None)

    return render(request, 'product_guide/product_base_v2.html', context=context)


@login_required()
def delete_line(request):
    product_number = int(request.POST.get('product.number'))
    print('delete product_number = ', product_number)
    product_dict_dicts, product_list = None, None

    if request.method == 'POST':
        product_dict_dicts = request.session['product_objects_dict_for_view']

        for product_key, product_value in product_dict_dicts.items():

            if product_value['number'] == product_number:
                product_dict_dicts.pop(product_key)
                break

        request.session['product_objects_dict_for_view'] = product_dict_dicts

    context = get_context_for_product_list(product_dict_dicts, page_num=None)

    return render(request, 'product_guide/show_giis_report.html', context=context)


def save_changes(request):
    request_obj = createRequestObject(request, 'SaveChanges')
    # Testing.show_context_data(request_obj.context, show_lists=True)
    return render(request, 'product_guide/product_base_v2.html', context=request_obj.context)
