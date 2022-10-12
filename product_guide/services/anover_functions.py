from django.core.paginator import Paginator


from product_guide.models import File
from django.core.exceptions import ObjectDoesNotExist
import xlrd

from product_guide.services.readers import read_excel_file
from product_guide.services.validity import isfloat


def search_query_processing(search_string):
    prod_name = prod_metal = prod_uin = prod_id = prod_art = prod_weight = None
    split_search_string = search_string.lower().split(' ')
    for string_element in split_search_string:
        if string_element.isdigit():
            if len(string_element) == 13:
                prod_id = string_element
            elif len(string_element) == 16:
                prod_uin = string_element
    return prod_name, prod_metal, prod_uin, prod_id, prod_art, prod_weight


def calculate_weight_number_price(products_dicts_dict):
    # print(products_dicts_dict)
    counter = 0
    total_weight = 0
    total_price = 0
    for key, product in products_dicts_dict.items():
        # print(product['weight'], type(product['weight']))
        # print(product)
        counter += 1
        try:
            if isfloat(product['weight']):

                total_weight += float(product['weight'])
        except:
            pass
    return total_weight, counter


def get_context_for_product_list(products_dicts_dict, page_num):
    counter = 0
    total_weight, number_of_products = calculate_weight_number_price(products_dicts_dict)
    product_queryset = make_product_queryset_from_dict_dicts(products_dicts_dict)
    # print('NUM =', page_num)
    # print(products_dicts_dict)
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
    try:
        file = File.objects.get(title=file_name)
        file.delete()
    except ObjectDoesNotExist:
        pass

    form.save()
    file_object = File.objects.latest('id')
    file_object.title = file_name
    file_object.save()


def form_type_check(rows_list, sheet, file_name):
    if file_name == '4_BATCH_LIST_PRINT.xlsx':
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

        # product_dict_for_view[counter] = product_dict_from_dbqueryset.values()
        # product_dict_for_view[counter] = {'name': product_dict_from_dbqueryset['name'],
        #                                   'metal': product_dict_from_dbqueryset['metal'],
        #                                   'barcode': product_dict_from_dbqueryset['barcode'],
        #                                   'uin': product_dict_from_dbqueryset['uin'],
        #                                   'weight': product_dict_from_dbqueryset['weight'],
        #                                   'vendor_code': product_dict_from_dbqueryset['vendor_code'],
        #                                   'size': product_dict_from_dbqueryset['size'],
        #                                   'price': product_dict_from_dbqueryset['price'],
        #                                   'number': counter
        #                                   }
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
    # print(outgoing_invoice_title_list)
    return outgoing_invoice_title_list

