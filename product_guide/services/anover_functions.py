import os
from django.core.paginator import Paginator

from jewelry_store_management.settings import BASE_DIR
from product_guide.models import File, Counterparties, Jewelry, Provider, IncomingInvoice
from product_guide.services.finders import find_name, find_metal, find_art, find_weight
from product_guide.services.validity import isfloat, check_weight, check_id, check_uin
from openpyxl import Workbook


def search_query_processing(search_string):
    name = metal = uin = barcode = vendor_code = weight = 'all'
    split_search_string = search_string.lower().split(' ')

    for string_element in split_search_string:
        if string_element.isdigit():
            if barcode == 'all':
                if check_id(string_element):
                    barcode = string_element
            if uin == 'all':
                if check_uin(string_element):
                    uin = string_element
        string_element = string_element.replace(',', '.') if ',' in string_element else string_element
        weight = string_element if isfloat(string_element) and weight == 'all' and check_weight(string_element) \
            else weight

        if name == 'all':
            name = find_name(string_element) if find_name(string_element) else name
        if metal == 'all':
            metal = find_metal(string_element) if find_metal(string_element) else metal
        if vendor_code == 'all':
            vendor_code = find_art(string_element, group=None) if (
                    find_art(string_element, group=None) and
                    check_id(string_element) is False and
                    check_uin(string_element is False)
            ) else vendor_code

    filters_dict = {
        'name': name,
        'metal': metal,
        'uin': uin,
        'barcode': barcode,
        'vendor_code': vendor_code,
        'weight': weight

    }
    print('filters_dict = ', filters_dict)
    return filters_dict


def save_invoice(form, file_name):
    file = File.get_object('title', file_name)
    file.delete()
    form.save()
    file_object = File.objects.latest('id')
    file_object.title = file_name
    file_object.save()

def make_product_dict_from_paginator(paginator):
    product_dict = {}
    count = paginator.count
    for c in range(count):
        product_list = paginator.get_page(c + 1)
        for product in product_list.object_list:
            for key, value in product.items():
                product_dict[key] = value

    return product_dict


def make_product_queryset_from_dict_dicts(dict_dicts):
    product_queryset = []
    for key, product in dict_dicts.items():
        product_queryset.append(product)

    return product_queryset


def make_product_dict_from_dbqueryset(dbqueryset):
    """ Функция создания словаря, для отображения в представлениях.
        Принимает QuerySet из базы данных и возвращает словарь словарей изделий с органиченным набором ключей."""

    product_dict_for_view, product_dicts_dict = {}, {}
    counter = 0

    for product_dict_from_dbqueryset in dbqueryset:
        counter += 1
        product_dict_from_dbqueryset['number'] = counter
        product_dicts_dict[counter] = product_dict_from_dbqueryset

    return product_dicts_dict


def has_filters_check(filters_dict):
    status = False
    for value in filters_dict.values():
        if value != 'all':
            status = True
    return status


def get_outgoing_invoice_title_list(out_inv_queryset):
    outgoing_invoice_title_list = []

    for invoice in out_inv_queryset.values():
        outgoing_invoice_title_list.append(invoice['title'])

    return outgoing_invoice_title_list


def get_files_title_list(files_queryset):
    files_title_list = []

    for file in files_queryset.values():
        files_title_list.append(file['title'])

    return files_title_list


def definition_of_invoice_type(provider, recipient):
    provider_id, invoice_type, recipient_id = None, None, None
    counterparties_queryset = Counterparties.get_all_obj()

    for counterparties_object in counterparties_queryset:
        if provider.find(counterparties_object.surname.lower()) != -1:
            provider_id = counterparties_object.id
        if recipient.find(counterparties_object.surname.lower()) != -1:
            recipient_id = counterparties_object.id
            invoice_type = 'incoming' if Counterparties.get_object('id',
                                                                   recipient_id).surname == 'Александрова' else 'outgoing'

    return invoice_type, provider_id, recipient_id


def create_nomenclature_file(file_path, products_dict_dict, invoice_dict):
    path = os.path.split(file_path)[0]
    path_for_save = path + 'Номенклатура для ' + os.path.split(file_path)[1].split('.')[0] + '.xlsx'
    nomenclature_file = Workbook()
    worksheet = nomenclature_file.active
    invoice_number = invoice_dict['invoice_number']
    provider = Counterparties.get_object('id', invoice_dict['provider_id']).surname
    number = None
    for number, product in products_dict_dict.items():
        number = number
        name = product['name']
        metal = product['metal']
        weight = product['weight']
        barcode = product['barcode']
        vendor_code = product['vendor_code']
        uin = product['uin']
        size = product['size']
        prod_description = f'{name}, {metal} (арт. {vendor_code}, уин {uin}, вес {weight} г.'
        if size:
            prod_description += f', р-р {size})'
        else:
            prod_description += ')'

        worksheet['A' + str(number)] = prod_description
        worksheet['B' + str(number)] = barcode
        worksheet['C' + str(number)] = vendor_code
        worksheet['D' + str(number)] = 'Товар'
        worksheet['E' + str(number)] = product['price']
        worksheet['F' + str(number)] = provider
        worksheet['G' + str(number)] = 'шт'
        worksheet['H' + str(number)] = '1'
        worksheet['I' + str(number)] = invoice_dict['arrival_date']
        worksheet['J' + str(number)] = f'Накладная {invoice_number}, {metal}'
    nomenclature_file.save(path_for_save)
    return path_for_save


def find_products_in_db(products_dicts_dict):
    def add_object(new_product_dicts_dict, funded_object):
        new_product_dicts_dict[number] = []
        for obj in funded_object:
            del obj._state
            obj.number = int(number)
            new_product_dicts_dict[number].append(obj.__dict__)
        return new_product_dicts_dict

    obj = None
    new_product_list = []
    new_product_dicts_dict = {}
    for number, product_dict in products_dicts_dict.items():
        if product_dict['barcode']:
            funded_object = Jewelry.get_object('barcode', product_dict['barcode'])
            if funded_object:
                del funded_object._state
                funded_object.number = int(number)
                new_product_dicts_dict[number] = funded_object.__dict__
        if number not in new_product_dicts_dict.keys():
            if product_dict['vendor_code']:
                funded_object = Jewelry.objects.filter(name=product_dict['name'],
                                                       metal=product_dict['metal'], weight=product_dict['weight'],
                                                       vendor_code=product_dict['vendor_code'])
                if funded_object:
                    new_product_dicts_dict = add_object(new_product_dicts_dict, funded_object)
            if number not in new_product_dicts_dict.keys():
                funded_object = Jewelry.objects.filter(name=product_dict['name'], metal=product_dict['metal'],
                                                       weight=float(product_dict['weight']))
                if funded_object:
                    new_product_dicts_dict = add_object(new_product_dicts_dict, funded_object)
            if number not in new_product_dicts_dict.keys():
                funded_object = Jewelry.objects.filter(name=product_dict['name'], weight=float(product_dict['weight']))
                if funded_object:
                    new_product_dicts_dict = add_object(new_product_dicts_dict, funded_object)
            if number not in new_product_dicts_dict.keys():
                funded_object = Jewelry.objects.filter(metal=product_dict['metal'],
                                                       weight=float(product_dict['weight']))
                if funded_object:
                    new_product_dicts_dict = add_object(new_product_dicts_dict, funded_object)
            if number not in new_product_dicts_dict.keys():
                funded_object = Jewelry.objects.filter(weight=float(product_dict['weight']))
                if funded_object:
                    new_product_dicts_dict = add_object(new_product_dicts_dict, funded_object)

    for product in new_product_dicts_dict.values():

        if not isinstance(product, list):
            new_product_list.append(product)
        else:
            for prod in product:
                new_product_list.append(prod)

    return new_product_list


def get_or_save_provider(invoice_data):
    counterparties_obj = Counterparties.get_object('id', invoice_data['provider_id'])
    # print('counterparties_obj = ', counterparties_obj.__dict__)
    if counterparties_obj:
        provider_surname = counterparties_obj.surname
        provider_obj = Provider.get_object('title', provider_surname)

        if not provider_obj:
            provider_obj = Provider()
            provider_obj.title = provider_surname
            provider_obj.counterparties_id = counterparties_obj.id
            provider_obj.save()

        return provider_obj


def get_or_save_input_invoice_obj(invoice_data, provider_obj):
    input_invoice_obj = InputInvoice.get_object('title', invoice_data['title'])
    if not input_invoice_obj:
        input_invoice_obj = InputInvoice()
        input_invoice_obj.provider_id = provider_obj.id
        input_invoice_obj.arrival_date = invoice_data['arrival_date']
        input_invoice_obj.save()