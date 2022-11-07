import os
from django.core.paginator import Paginator
from product_guide.models import File, Counterparties, Jewelry
from product_guide.services.finders import find_name, find_metal, find_art, find_weight
from product_guide.services.validity import isfloat
from openpyxl import Workbook


def search_query_processing(search_string):
    prod_name = prod_metal = prod_uin = prod_id = prod_art = prod_weight = 'all'
    split_search_string = search_string.lower().split(' ')

    for string_element in split_search_string:
        if string_element.isdigit():
            if prod_id == 'all':
                if len(string_element) == 13 or len(string_element) == 10:
                    prod_id = string_element
            if prod_uin == 'all':
                if len(string_element) == 16:
                    prod_uin = string_element
        string_element = string_element.replace(',', '.') if ',' in string_element else string_element
        prod_weight = float(string_element) if isfloat(string_element) and prod_weight == 'all' else string_element

        if prod_name == 'all':
            prod_name = find_name(string_element) if find_name(string_element) else prod_name
        if prod_metal == 'all':
            prod_metal = find_metal(string_element) if find_metal(string_element) else prod_metal
        if prod_art == 'all':
            prod_art = find_art(string_element, group=None) if find_art(string_element, group=None) else prod_art

    print('prod_name = ', prod_name)
    print('prod_metal = ', prod_metal)
    print('prod_uin = ', prod_uin)
    print('prod_id = ', prod_id)
    print('prod_art = ', prod_art)
    print('prod_weight = ', prod_weight)

    return prod_name, prod_metal, prod_uin, prod_id, prod_art, prod_weight


def calculate_weight_number_price(products_dicts_dict):
    counter = 0
    total_weight = 0

    for key, product in products_dicts_dict.items():

        counter += 1
        try:
            if isfloat(product['weight']):
                total_weight += float(product['weight'])
        except:
            pass

    return total_weight, counter


def get_context_for_product_list(products_dicts_dict, page_num):
    total_weight, number_of_products = calculate_weight_number_price(products_dicts_dict)
    product_queryset = make_product_queryset_from_dict_dicts(products_dicts_dict)
    product_list = []
    paginator = Paginator(product_queryset, 50)
    page = paginator.get_page(page_num)
    context = {
        'product_list': page.object_list,
        'list_length': len(product_list),
        'num_pages': [x for x in range(paginator.num_pages + 1)][1:],
        'total_weight': round(total_weight, ndigits=2),
        'len_products': number_of_products
    }
    return context


def save_invoice(form, file_name):

    file = File.get_object('title', file_name)
    file.delete()
    form.save()
    file_object = File.objects.latest('id')
    file_object.title = file_name
    file_object.save()


def form_type_check(file_name):
    if file_name.startswith('4_BATCH_LIST_PRINT'):
        return 'giis_report'


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


def filters_check(product_name, product_metal):
    if product_name == 'all' and product_metal == 'all':
        return 'all'
    else:
        return 'filtered'


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
            invoice_type = 'incoming' if Counterparties.get_object('id', recipient_id).surname == 'Александрова' else 'outgoing'

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
    obj = None
    counter = 0
    new_product_list = []

    for product in products_dicts_dict.values():
        new_product_dicts_dict = {}
        objs_list = []
        counter += 1

        new_product_dicts_dict[counter] = product
        if product['barcode']:
            obj = Jewelry.objects.filter(barcode=product['barcode'])

            if obj:
                new_product_dicts_dict[counter] = obj.__dict__
            else:
                if product['vendor_code']:
                    objs = Jewelry.objects.filter(name=product['name'], metal=product['metal'], weight=product['weight'], vendor_code=product['vendor_code'])
                    if objs:
                        for obj in objs:
                            objs_list.append(obj.__dict__)
                        new_product_dicts_dict[counter] = objs_list
        if counter not in new_product_dicts_dict.keys():
            objs = Jewelry.objects.filter(name=product['name'], metal=product['metal'], weight=product['weight'])
            if objs:
                for obj in objs:
                    objs_list.append(obj.__dict__)
                new_product_dicts_dict[counter] = objs_list
        new_product_list.append(new_product_dicts_dict)

    for product in new_product_list:
        print(product)



