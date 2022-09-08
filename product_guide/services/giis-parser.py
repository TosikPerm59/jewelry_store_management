import openpyxl
import warnings
from allFinders import find_art, find_description, find_weight
from validity import check_id
from servise_files import excelReader

warnings.simplefilter("ignore")


def find_id(*description):
    """ Функция ищет в описании и наименовании позиции, строку состоящую из 13 символов и состоящую
    только из цифр.
        Возвращает строку или None """

    for elem in description:
        elem = str(elem)
        for part in elem.split(' '):
            if check_id(part):
                return part


def giis_file_parsing(path_to_giis_file):
    """ Функция анализа файла Excel сформированного платформой ГИИС ДМДК.
      На вход функция принимает путь к файлу, который необходимо обработать. Так как, данные из портала ГИИС ДМДК
    заполняются разными людьми, то и формат записи и порядок заполнения не имеет четкой последовательности. Для того
    что бы все позиции имели структурированные характеристики, функция проходит построчно по таблице
    и анализируя данные принимает решение о помещении этих данных соответствующим ключам словаря принадлежащего
    текущей позиции.
      Функция возвращает словарь с позициями в которых все характеристики упорядочены и проверены. """

    giis_list = []
    rows_list, sheet, file_type, file_name, file_path = excelReader.read_excel_file(path_to_giis_file)
    group = 'excel'
    rows_list = rows_list[4:]
    counter = 0

    # Выполняется построчный проход по таблице
    for row in rows_list:
        counter += 1
        uin = sheet[row][1].value
        _id = find_id(sheet[row][10].value, sheet[row][11].value)
        art = find_art(sheet[row][10].value, sheet[row][11].value, group=group)
        descr = find_description(sheet[row][10].value, sheet[row][11].value, sheet[row][14].value,
                                 sheet[row][23].value, group=group)
        weight = find_weight([sheet[row][12].value])

        giis_dict = {uin: {}}
        if _id:
            giis_dict[uin]['ID'] = _id
        if art:
            giis_dict[uin]['Артикул'] = art

        giis_dict[uin]['Описание'] = descr
        giis_dict[uin]['Масса'] = weight + ' гр'

        giis_list.append(giis_dict)
    print(f'Сформирован список изделии файла ГИИС из {counter} позиций')
    return giis_list


# # Test
# giis_list = giis_file_parsing("E:\Elena\Downloads\\batches_list.xlsx")
# #
# counter = 0
# for item in giis_list:
#     counter += 1
#     print(f'Строка {counter} --- {item.items()}')
