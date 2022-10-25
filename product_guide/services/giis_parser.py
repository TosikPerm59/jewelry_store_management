import openpyxl
import warnings
from .finders import find_art, find_description, find_weight, find_id
from .validity import check_id

warnings.simplefilter("ignore")


def giis_file_parsing(rows_list, sheet):
    """ Функция анализа файла Excel сформированного платформой ГИИС ДМДК.
      На вход функция принимает путь к файлу, который необходимо обработать. Так как, данные из портала ГИИС ДМДК
    заполняются разными людьми, то и формат записи и порядок заполнения не имеет четкой последовательности. Для того
    что бы все позиции имели структурированные характеристики, функция проходит построчно по таблице
    и анализируя данные принимает решение о помещении этих данных соответствующим ключам словаря принадлежащего
    текущей позиции.
      Функция возвращает словарь с позициями в которых все характеристики упорядочены и проверены. """

    giis_dicts_dict = {}
    group = 'excel'
    rows_list = rows_list[4:]
    counter = 0

    # Выполняется построчный проход по таблице
    for row in rows_list:
        counter += 1
        description = find_description(sheet[row][10].value, sheet[row][11].value, sheet[row][14].value,
                                       sheet[row][23].value, group=group)

        barcode = find_id(sheet[row][10].value, sheet[row][11].value) if find_id(sheet[row][10].value, sheet[row][11].value) else None
        uin = sheet[row][1].value if sheet[row][1].value else None
        vendor_code = find_art(sheet[row][10].value, sheet[row][11].value, group=group) if find_art(sheet[row][10].value, sheet[row][11].value, group=group) else None
        size = description['size'] if description['size'] else None
        product_dict = {'name': description['name'],
                        'metal': description['metal'],
                        'barcode': barcode,
                        'uin': uin,
                        'weight': find_weight([sheet[row][12].value]),
                        'vendor_code': vendor_code,
                        'size': size,

                        'number': counter
                        }

        giis_dicts_dict[counter] = product_dict
        print(counter, product_dict)

    print(f'Сформирован список изделии файла ГИИС из {counter} позиций')
    return giis_dicts_dict


