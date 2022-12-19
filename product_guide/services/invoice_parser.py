from product_guide.models import Counterparties, Provider, Recipient
from product_guide.services.anover_functions import definition_of_invoice_type
from product_guide.services.finders import *
invoice_requisites = {}


def invoice_parsing(full_rows_list, sheet, file_type, file_name):
    uin_ind = product_ind = weight_ind = price_ind = prod_uin = price_per_gram_ind = start = finish \
        = provider = row_with_date_index = invoice_number = invoice_date = col_with_number \
        = col_with_date = code_ind = prod_barcode_from_giis = prod_weight = prod_name = prod_barcode = prod_art \
        = prod_price = recipient_id = provider_id = recipient = None
    counter = 0
    product_list, product_dicts_dict = [], {}
    string_with_provider = string_with_recipient = ''
    if file_type == '.xlsx':
        cols = sheet.max_column
        rows_lst = []
        for row in full_rows_list:
            row_lst = []
            for col in range(cols):
                cell_text = sheet[row][col].value
                if isinstance(cell_text, str):
                    cell_text = cell_text.replace('\n', '').lower() if '\n' in cell_text else cell_text.lower()
                row_lst.append(cell_text)
            rows_lst.append(row_lst)
        full_rows_list = rows_lst

    for row in full_rows_list:
        if 'поставщик' in row:
            # print(row)
            for elem in row:
                if isinstance(elem, str) and elem != '' and elem is not None:
                    string_with_provider += elem + ' '
        if 'грузополучатель' in row or 'плательщик' in row:
            for elem in row:
                if isinstance(elem, str) and elem != '' and elem is not None:
                    string_with_recipient += elem + ' '
        if 'товарная накладная  ' in row or 'товарная накладная ' in row:
            # print(row)
            invoice_date = row[15]
            if invoice_date is None or invoice_date == '':
                invoice_date = row[21]
                if invoice_date is None or invoice_date == '':
                    invoice_date = row[13]
                    # print(row[13])
                    # print(invoice_date)
            invoice_number = row[12]
            if invoice_number is None or invoice_number == '':
                invoice_number = row[18]
                if invoice_number is None or invoice_number == '':
                    invoice_number = row[8]
                    # print(invoice_number)
        if 'страница 1' in row:
            start = counter + 1
        if 'всего по накладной ' in row:
            finish = counter
            break
        counter += 1

    counter = 0

    header = full_rows_list[start: start + 2]

    for row in header:
        # print(row)
        for elem in row:
            if isinstance(elem, str) and elem != '':
                changed_elem = elem.replace('\n', ' ') if '\n' in elem else elem

                if changed_elem.find('наименование') != -1:
                    product_ind = row.index(elem)

                if changed_elem.find('нетто') != -1:
                    weight_ind = row.index(elem)

                if changed_elem.find('сумма с учетом') != -1 or changed_elem.find('сумма сучетом') != -1:
                    price_ind = row.index(elem)

                if changed_elem.find('цена') != -1:
                    price_per_gram_ind = row.index(elem)

                if changed_elem.find('уин') != -1:
                    uin_ind = row.index(elem)

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
                if file_type == '.xls':
                    descr += (row_3[2] + ' ' + row_3[12] + ' ').lower()
                else:
                    descr += (row_3[2] + ' ' + row_3[6] + ' ').lower() if row_3[6] is not None else ''
                    descr += (row_3[2] + ' ' + row_3[12] + ' ').lower() if row_3[12] is not None else ''

            descr = descr.replace('\n', ' ') if '\n' in descr else descr
            descr = descr.replace('шк:', ' ') if 'шк:' in descr else descr
            descr = descr.replace('бирка:', ' ') if 'бирка:' in descr else descr
            descr = descr.replace('  ', ' ') if '  ' in descr else descr
            row[2] = descr
            product_list.append(row)

    for product in product_list:
        # print(product)

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

        if prod_uin is None:
            if prod_barcode is not None:
                pass

        if prod_metal is None:
            price_per_gram = prod_price / prod_weight
            if price_per_gram > 2500:
                prod_metal = 'Золото 585'
            else:
                prod_metal = 'Серебро 925'

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
        # print(product_dict)
        product_dicts_dict[counter] = product_dict

    invoice_type, provider_id, recipient_id = definition_of_invoice_type(string_with_provider, string_with_recipient)

    invoice_requisites['provider_id'] = provider_id
    invoice_requisites['recipient_id'] = recipient_id
    invoice_requisites['invoice_date'] = invoice_date
    invoice_requisites['invoice_number'] = invoice_number
    invoice_requisites['invoice_type'] = invoice_type
    return product_dicts_dict, invoice_requisites


def word_invoice_parsing(header_table, product_table):
    counterparties_objs = Counterparties.get_all_obj()
    providers_objs = Provider.get_all_obj()
    recipient_objs = Recipient.get_all_obj()
    max_row_product_table = len(product_table.rows)
    max_row_header_table = len(header_table.rows)
    products_dicts_dict = {}
    counter = 0
    part_list = []

    provider_id, recipient_id = None, None

    for row in range(max_row_header_table):

        for cell in range(7):
            text = header_table.rows[row].cells[cell].text
            if len(part_list) == 0:
                part_list.append(text)
            elif part_list[-1] != text:
                part_list.append(text)

    for elem in part_list:
        if elem == 'Поставщик':
            provider_index = part_list.index(elem) + 1
            provider_string = part_list[provider_index]

            for counterparty in counterparties_objs:
                if counterparty.surname in provider_string:
                    for provider_obj in providers_objs:
                        if provider_obj.counterparties == counterparty:
                            provider_id = provider_obj.id
                            break
                    else:
                        provider_obj = Provider()
                        provider_obj.title = counterparty.surname
                        provider_obj.counterparties = counterparty
                        provider_obj.save()
                        provider_id = provider_obj.id

        elif elem == 'Грузополучатель':
            recipient_index = part_list.index(elem) + 1
            recipient_string = part_list[recipient_index]
            for counterparty in counterparties_objs:
                if counterparty.surname in recipient_string:
                    for recipient_obj in recipient_objs:
                        if recipient_obj.counterparties == counterparty:
                            recipient_id = recipient_obj.id
                            break
                    else:
                        recipient_obj = Recipient()
                        recipient_obj.title = counterparty.surname
                        recipient_obj.counterparties = counterparty
                        recipient_obj.save()
                        recipient_id = recipient_obj.id


    invoice_requisites['provider_id'] = provider_id
    invoice_requisites['recipient_id'] = recipient_id
    invoice_requisites['invoice_date'] = part_list[-2]
    invoice_requisites['invoice_number'] = part_list[-3]

    for row in range(3, max_row_product_table - 21):
        counter += 1
        string = product_table.rows[row].cells[4].text.lower()
        string = string.replace(',', '') if ',' in string else string
        string = string.replace('(', '') if '(' in string else string
        string = string.replace(')', '') if ')' in string else string
        split_string = string.split(' ')
        price = product_table.rows[row].cells[45].text.lower()
        price = price.replace(',', '.') if ',' in price else price
        price = price.replace(' ', '') if ' ' in price else price
        price = price.replace('\xa0', '') if '\xa0' in price else price
        products_dicts_dict[counter] = {
            'weight': find_weight(split_string),
            'size': find_size(split_string, group='word'),
            'name': find_name(split_string),
            'metal': find_metal(split_string),
            'uin': find_uin_in_string(split_string),
            'vendor_code': find_art(split_string, group=None),
            'number': counter,
            'barcode': None,
            'price': float(price) if isfloat(price) else ''
        }
    # print(products_dicts_dict)
    return products_dicts_dict, invoice_requisites
