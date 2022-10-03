from product_guide.models import File
from django.core.exceptions import ObjectDoesNotExist
import xlrd


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


def make_product_dict_from_dbqueryset(dbqueryset):

    """ Функция создания словаря, для отображения в представлениях.
        Принимает QuerySet из базы данных и возвращает словарь словарей изделий с органиченным набором ключей."""

    product_dict_for_view, product_dicts_dict = {}, {}
    counter = 0
    for product_dict_from_dbqueryset in dbqueryset.values():
        counter += 1
        product_dict_for_view[counter] = {'name': product_dict_from_dbqueryset['name'],
                                          'metal': product_dict_from_dbqueryset['metal'],
                                          'barcode': product_dict_from_dbqueryset['barcode'],
                                          'uin': product_dict_from_dbqueryset['uin'],
                                          'weight': product_dict_from_dbqueryset['weight'],
                                          'vendor_code': product_dict_from_dbqueryset['vendor_code'],
                                          'size': product_dict_from_dbqueryset['size'],
                                          'price': product_dict_from_dbqueryset['price'],
                                          'number': counter
                                          }
        product_dicts_dict[counter] = product_dict_from_dbqueryset

    return product_dicts_dict


def calculate_weight_number_price(product_list):
    counter = 0
    total_weight = 0
    total_price = 0
    for product in product_list:
        counter += 1
        if type(product['weight']) is float:
            total_weight += product['weight']
    return total_weight, counter


def get_context_for_product_list(product_list):
    counter = 0
    total_weight, number_of_products = calculate_weight_number_price(product_list)

    for product in product_list:
        counter += 1
        product['number'] = counter

    context = {
        'product_list': product_list,
        'list_length': len(product_list),
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


# def form_type_check(invoice_path):
#     document = docx.Document(invoice_path)
#     print(document.paragraphs[0].text)
#     if 'Унифицированная форма № ТОРГ-12' in document.paragraphs[0].text:
#         if len(document.paragraphs) == 3:
#             return 'Торг12'