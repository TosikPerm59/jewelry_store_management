
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


def make_dict_from_list(product_list):
    product_dict = {}
    counter = 0
    for product in product_list:
        counter += 1
        product_dict[counter] = product

    return product_dict


def make_product_dict_from_dbqueryset(dbqueryset):
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
                                          'product_number': counter
                                          }
        product_dicts_dict[counter] = product_dict_from_dbqueryset

    return product_dicts_dict


def calculate_weight_number_price(product_list):
    counter = 0
    total_weight = 0
    total_price = 0
    for product in product_list:
        print(product)
        counter += 1
        if type(product['weight']) is float:
            total_weight += product['weight']
    return total_weight, counter


def get_context_for_product_list(product_list):
    total_weight, number_of_products = calculate_weight_number_price(product_list)
    context = {
        'product_list': product_list,
        'list_length': len(product_list),
        'total_weight': total_weight,
        'len_products': number_of_products
    }

    return context
