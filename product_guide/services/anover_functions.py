
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

