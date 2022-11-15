import warnings
from .finders import find_art, find_description, find_weight, find_id
from ..models import Jewelry, Manufacturer

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
    kits_dict = {}
    uin_list = []
    products_queryset = Jewelry.get_all_obj()
    manufacturers = Manufacturer.get_all_values_list('inn')

    for product in products_queryset:
        uin_list.append(product.uin)
    # Выполняется построчный проход по таблице
    for row in rows_list:
        manufacturer_id = None
        description, size, barcode, vendor_code, weight, giis_status = None, None, None, None, None, None
        uin = sheet[row][1].value if sheet[row][1].value else None
        uin2 = sheet[row][2].value if sheet[row][2].value else None
        uins = None
        giis_status = sheet[row][6].value if sheet[row][6].value else None
        if giis_status == 'Терминальная стадия':
            giis_status = 'Выбыл'
            availability_status = 'Продано'
        else:
            availability_status = 'В наличии'
        manufacturer_inn = sheet[row][9].value if sheet[row][9].value != '0000000000' else None
        if manufacturer_inn:
            if manufacturer_inn not in manufacturers:
                manufacturers.append(manufacturer_inn)
                manufacturer = Manufacturer(inn=manufacturer_inn)
                manufacturer.save()
            manufacturer = Manufacturer.get_object('inn', str(manufacturer_inn))
            if manufacturer:
                manufacturer_id = manufacturer.id
        counter += 1
        if uin2:
            if uin2 not in kits_dict.keys():
                kits_dict[uin2] = {'weight': find_weight([sheet[row][12].value]), 'uin1': uin}
                continue
        if uin:
            if int(uin) not in uin_list:
                description = find_description(sheet[row][10].value, sheet[row][11].value, sheet[row][14].value,
                                               sheet[row][23].value, group=group)
                barcode = find_id(sheet[row][10].value, sheet[row][11].value) if find_id(sheet[row][10].value,
                                                                                         sheet[row][11].value) else None
                vendor_code = find_art(sheet[row][10].value, sheet[row][11].value, group=group) if find_art(
                    sheet[row][10].value, sheet[row][11].value, group=group) else None
                size = description['size'] if description['size'] else None
                coating = None
                if uin2 in kits_dict.keys():
                    weight = float(find_weight([sheet[row][12].value])) + float(kits_dict[uin2]['weight'])
                    uins = [uin, kits_dict[uin2]['uin1']]
                    uin = uin2
                else:
                    weight = find_weight([sheet[row][12].value])
            else:
                obj = Jewelry.get_object('uin', int(uin))
                description = {
                    'name': obj.name,
                    'metal': obj.metal
                }
                weight = obj.weight
                vendor_code = obj.vendor_code
                size = obj.size
                barcode = obj.barcode

        product_dict = {'name': description['name'],
                        'metal': description['metal'],
                        'barcode': barcode,
                        'uin': uin,
                        'weight': weight,
                        'vendor_code': vendor_code,
                        'size': size,
                        'number': counter,
                        'uins': uins,
                        'giis_status': giis_status,
                        'availability_status': availability_status,
                        'manufacturer_id': manufacturer_id
                        }

        giis_dicts_dict[counter] = product_dict
        print(counter, product_dict)

    print(f'Сформирован список изделии файла ГИИС из {counter} позиций')
    return giis_dicts_dict
