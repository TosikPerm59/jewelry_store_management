from product_guide.models import Jewelry, Metal, File
from product_guide.services.finders import *
from product_guide.services.readers import read_excel_file


def invoice_parsing(path_to_excel_file):
    full_rows_list, sheet, file_type, file_name, file_path = read_excel_file(path_to_excel_file)
    uin_ind = product_ind = weight_ind = price_ind = prod_uin = price_per_gram_ind = start = finish \
        = row_with_provider_index = provider = row_with_date_index = invoice_number = invoice_date = col_with_number \
        = col_with_date = code_ind = prod_barcode_from_giis = prod_weight = prod_name = prod_barcode = prod_art \
        = prod_price = prod_metal = prod_size = None

    products_with_size = {'кольцо': 'кольца', 'цепь': 'цепи', 'браслет': 'браслета', 'колье': 'колье', 'конго': 'конго'}
    counter = 0
    product_list, product_dicts_dict = [], {}
    provaiders = {'Степин': ['590500827512'],
                  'Белышева': ['590202863882'],
                  'Мидас': ['5904148360', '5902179700']}

    if file_type == '.xlsx':
        cols = sheet.max_column
        rows_lst = []
        for row in full_rows_list:
            row_lst = []
            for col in range(cols):
                cell_text = sheet[row][col].value
                if isinstance(cell_text, str):
                    cell_text = cell_text.lower()
                row_lst.append(cell_text)
            rows_lst.append(row_lst)
        full_rows_list = rows_lst

    for row in full_rows_list:
        counter += 1
        if 'форма по окуд ' in row:
            if 'инн' in row:
                row_with_provider_index = counter - 1
            else:
                row_with_provider_index = counter - 2
        if 'товарная накладная  ' in row or 'товарная накладная ' in row:
            row_with_date_index = counter - 1
        if 'страница 1' in row:
            start = counter
        if 'всего по накладной ' in row:
            finish = counter - 1
            break
    counter = 0

    row_with_provider = []
    for elem in full_rows_list[row_with_provider_index]:
        if elem is not None:
            row_with_provider.append(elem)
    for key, values in provaiders.items():
        for value in values:
            if value in ''.join(row_with_provider):
                provider = key
                break
        if provider:
            break

    col_with_number = full_rows_list[row_with_date_index - 1].index('номер документа')
    col_with_date = full_rows_list[row_with_date_index - 1].index('дата составления')
    invoice_number = full_rows_list[row_with_date_index][col_with_number]
    invoice_date = full_rows_list[row_with_date_index][col_with_date]
    header = full_rows_list[start: start + 2]
    input_invoice = File.objects.get(title=file_name)

    for row in header:
        for elem in row:
            if elem is not None:
                origin_elem = elem
                elem = str(elem)
                r_elem = ''
                if '\n' in elem:
                    r_elem = elem.replace('\n', '')

                if r_elem.find('наименование') != -1 or elem.find('наименование') != -1:
                    product_ind = row.index(origin_elem)
                if r_elem.find('нетто') != -1 or elem.find('нетто') != -1:
                    weight_ind = row.index(origin_elem)
                if r_elem.find('сумма сучетом ндс') != -1 or elem.find('сумма сучетом ндс') != -1:
                    price_ind = row.index(origin_elem)
                if r_elem.find('цена') != -1 or elem.find('цена') != -1:
                    price_per_gram_ind = row.index(origin_elem)
                if r_elem.find('уин') != -1 or elem.find('уин') != -1:
                    uin_ind = row.index(origin_elem)
                if code_ind is None:
                    if r_elem.find('код') != -1 or elem.find('код') != -1:
                        code_ind = row.index(origin_elem)

    if file_type == '.xls':
        index_number = 1
        for row in full_rows_list[start + 3: finish]:
            descr = ''
            row_start_index, row_finish_index = None, None

            if isinteger(row[1]) and int(row[1]) == index_number or isfloat(row[1]) and int(row[1]) == index_number:
                index_number += 1
                row_start_index = full_rows_list.index(row)
                for row_2 in full_rows_list[row_start_index + 1: finish]:
                    if (isinteger(row_2[1]) and int(row_2[1]) == int(row[1]) + 1 or isfloat(row_2[1])
                            and int(row_2[1]) == int(row[1]) + 1 or 'итого ' in row_2):
                        row_finish_index = full_rows_list.index(row_2)
                        break

                for row_3 in full_rows_list[row_start_index: row_finish_index]:
                    descr += (row_3[2] + ' ' + row_3[12] + ' ').lower()
                descr = descr.replace('\n', ' ') if '\n' in descr else descr
                descr = descr.replace('шк:', ' ') if 'шк:' in descr else descr
                descr = descr.replace('бирка:', ' ') if 'бирка:' in descr else descr
                descr = descr.replace('  ', ' ') if '  ' in descr else descr
                row[2] = descr
                product_list.append(row)

    if file_type == '.xlsx':
        product_list = full_rows_list[start + 3: finish]

    for product in product_list:


        if product[1] is None or not str(product[1]).isdigit():
            product[1] = '0'

        if file_type == '.xlsx' and int(product[1]) == counter + 1 or file_type == '.xls':

            counter += 1
            description_string = product[product_ind].lower()
            if '(' in description_string:
                description_string = description_string.replace('(', '')
            if ')' in description_string:
                description_string = description_string.replace(')', '')
            if ';' in description_string:
                description_string = description_string.replace(';', '')
            split_description_string = description_string.split(' ')

            prod_name = find_name(description_string)
            prod_metal = find_metal(description_string)
            prod_size = find_size(split_description_string, group='excel')
            prod_weight = product[weight_ind]
            prod_art = find_art(description_string, group='excel')
            prod_barcode = find_barcode(description_string)
            prod_price = product[price_ind]
            prod_uin = find_uin_in_string(description_string)
            if prod_barcode is None:
                if code_ind:
                    prod_barcode = find_barcode(product[code_ind])

            if prod_metal is None:
                if float(prod_price) / float(prod_weight) > 1000:
                    prod_metal = 'Золото 585'
                else:
                    prod_metal = 'Серебро 925'

            if uin_ind:
                prod_uin = find_uin_in_string(product[uin_ind])
            if prod_uin is None:
                prod_uin = find_uin_in_string(description_string)

            if not prod_metal:
                if product[price_per_gram_ind] > 2500:
                    prod_metal = 'Золото 585'
                else:
                    prod_metal = 'Серебро 925'

            product_characteristics = [prod_name, prod_metal, prod_weight, prod_barcode, prod_art, prod_uin, prod_price,
                                       prod_size]

            product_dict = {'name': prod_name,
                            'metal': prod_metal,
                            'barcode': prod_barcode,
                            'uin': prod_uin,
                            'weight': round(float(prod_weight), ndigits=2),
                            'vendor_code': prod_art,
                            'size': round(float(prod_size), ndigits=2) if isfloat(prod_size) else None,
                            'price': round(float(prod_price), ndigits=2),
                            'number': counter
                            }

            product_dicts_dict[counter] = product_dict

    return product_dicts_dict, invoice_date, invoice_number, provider,
