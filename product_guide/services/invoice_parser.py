from openpyxl import Workbook
from allFinders import *
from servise_files import giisParser, excelReader
from inputs import input_giis_file_path


def invoice_parsing(path_to_excel_file):

    full_rows_list, sheet, file_type, file_name, file_path = excelReader.read_excel_file(path_to_excel_file)
    uin_ind = product_ind = weight_ind = price_ind = prod_uin = price_per_gram_ind = start = finish\
        = row_with_provider_index = provider = row_with_date_index = invoice_number = invoice_date = col_with_number \
        = col_with_date = code_ind = prod_barcode_from_giis = None
    new_excel_file = Workbook()
    new_excel_sheet = new_excel_file.active
    products_with_size = {'кольцо': 'кольца', 'цепь': 'цепи', 'браслет': 'браслета', 'колье': 'колье', 'конго': 'конго'}
    giis_list = giisParser.giis_file_parsing(input_giis_file_path())
    counter = 0
    product_list = []
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

        for row in full_rows_list[start + 3: finish]:
            descr = ''
            row_start_index, row_finish_index = None, None
            if isinteger(row[1]) or isfloat(row[1]):

                row_start_index = full_rows_list.index(row)
                for row_2 in full_rows_list[row_start_index + 1: finish]:
                    if (isinteger(row_2[1]) and int(row_2[1]) == int(row[1]) + 1 or isfloat(row_2[1])
                            and int(row_2[1]) == int(row[1]) + 1 or 'Итого' in row_2):
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
            elif prod_barcode:
                prod_uin, string_number = find_uin_in_giis_list(_id=prod_barcode, _list=giis_list)
            if prod_uin is None:
                prod_uin = find_uin_in_string(description_string)
                if prod_uin is None:
                    prod_list = find_uin_in_giis_list(name=prod_name, metal=prod_metal, weight=prod_weight,
                                                      art=prod_art, _list=giis_list)
                    if prod_list:
                        if len(prod_list) == 1:
                            for key, value in prod_list[0].items():
                                prod_uin = key
                                if 'ID' in value:
                                    prod_barcode_from_giis = value['ID']

                        else:
                            print(f'\nВыполняется поиск УИН для изделия {prod_name, prod_metal, prod_art, prod_weight}.')
                            print(f'Найдено {len(prod_list)} строк с похожим описанием изделия')
                            count = 0
                            for prod in prod_list:
                                count += 1
                                print(f'Строка {count}: {prod}')
                            print('\nВыберите наиболее подходящую строку и введите ее номер.')
                            number = input('Введите номер строки или ENTER, чтобы пропустить выбор: ')
                            if number.isdigit():
                                for key, value in prod_list[int(number) - 1].items():
                                    prod_uin = key
                                    if 'ID' in value:
                                        prod_barcode_from_giis = value['ID']

                        if prod_barcode and prod_barcode_from_giis:
                            if prod_barcode_from_giis != prod_barcode:
                                prod_barcode = prod_barcode_from_giis

            if not prod_metal:
                if product[price_per_gram_ind] > 2500:
                    prod_metal = 'Золото 585'
                else:
                    prod_metal = 'Серебро 925'

            prod_description = f'{prod_name}, {prod_metal} ('

            if prod_art:
                prod_description = f'{prod_description}арт. {prod_art}'

            if prod_uin:
                prod_description = f'{prod_description}, уин {prod_uin}'
            prod_description = f'{prod_description}, вес {float(prod_weight)} г.'

            if prod_name is None:
                print(f'Программе не удалось определить имя изделия в строчке {description_string}.')
                prod_name = input('Введите название изделия: ')

            if prod_name.lower() in products_with_size.keys():
                if not prod_size:
                    print(f'\nПрограмме не удалось определить размер для {products_with_size[prod_name.lower()]}'
                          f' в строке {counter}.')
                    print(f'Укажите размер для изделия: {prod_description}')
                    prod_size = input('Введите размер в формате 00.0: ')
            if prod_size:
                prod_description = f'{prod_description}, р-р {prod_size}'
            prod_description = f'{prod_description})'
            print(prod_description, prod_barcode)

            """Принты для теста функции"""
            # print(prod_description, prod_barcode, prod_price, provider)

            new_excel_sheet['A' + str(counter)] = prod_description
            new_excel_sheet['B' + str(counter)] = str(prod_barcode)
            new_excel_sheet['C' + str(counter)] = prod_art
            new_excel_sheet['D' + str(counter)] = 'Товар'
            new_excel_sheet['E' + str(counter)] = prod_price
            new_excel_sheet['F' + str(counter)] = provider
            new_excel_sheet['G' + str(counter)] = 'шт'
            new_excel_sheet['H' + str(counter)] = '1'
            new_excel_sheet['I' + str(counter)] = f'{invoice_date}'
            new_excel_sheet['J' + str(counter)] = f'Накладная {invoice_number}, {prod_metal}'

        prod_name = prod_metal = prod_inserts = prod_weaving = prod_art = prod_uin = prod_barcode \
            = prod_barcode_from_giis = None

    path_for_save = f'{file_path}\\Номенклатура для({file_name}).xlsx'
    new_excel_file.save(path_for_save)

# Test
# invoice_parsing(
#     'E:\Elena\Documents\Документы  Александрова Е.П\Накладные\Входящие накладные\Степин Евгений\\05.09.22\965.xls')
