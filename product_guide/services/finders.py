from validity import *

# Варианты возможных размеров изделий
sizes = ['14.0', '14.5', '15.0', '15.5', '16.0', '16.5', '17.0', '17.5', '18.0', '18.5', '19.0', '19.5', '20.0',
         '20.5', '21.0', '21.5', '22.0', '22.5', '23.0', '23.5', '24.0', '24.5', '25.0', '30.0', '35.0', '38.0',
         '40.0', '42.0', '45.0', '50.0', '55.0', '60.0', '65.0', '70.0', '75.0']

# Варианты префиксов артикула изделия относящегося к цепям или браслетам
keywords = {'цепь': ['цб', 'нц', 'ци'], 'колье': ['шнурок'], 'браслет': ['бр', 'бк', 'нб', 'бб', 'бв', 'би']}

# Варианты плетений цепей и браслетов
keywords_weaving = {'перлина': ['шариковая', 'перлина'], 'сингапур': ['сингапур'], 'нонна': ['нонна'],
                    'якорь': ['якорь', 'якорное'], 'бисмарк': ['бисмарк'], 'фигаро': ['фигаро', 'картье'],
                    'снэйк': ['снэйк', 'снейк', 'кобра'], 'ромб': ['ромб'], 'love': ['love', 'лав', 'сердечки']}

# Варианты имен изделий
keywords_name = ['кольцо', 'цепь', 'серьги', 'подвеска', 'пусеты', 'браслет', 'крест', 'икона', 'колье', 'пирсинг',
                 'моно-серьга', 'ложка']

# Варианты вставок в изделия
keywords_inserts = {'аметистом': ['аметистом', 'аметист'], 'топазом': ['топазом', 'топаз'],
                    'аметрином': ['аметрином', 'аметрин'], 'празолитом': ['празолитом', 'празолит'],
                    'агатом': ['агатом', 'агат'], 'гранатом': ['гранатом', 'гранат'],
                    'фианитами': ['фианитом', 'фианит', 'фианитами'], 'турмалином': ['турмалином', 'турмалин'],
                    'топазом Лондон': ['Лондон', 'топаз лондон', 'топазом лондон'],
                    'ювелирным стеклом': ['стекло', 'ювелирное'], 'ониксом': ['ониксом'],
                    'наношпинделем': ['наношпиндель'], 'кристаллом Swarovski': ['кристалл swarovski', 'swarovski'],
                    'кристаллом премиум': ['кристалл премиум']}


def find_barcode(_string):
    spl_str = _string.split(' ')
    for elem in spl_str:
        if elem.startswith('(') and elem.endswith(')'):
            elem = elem[1: -1]
        if check_id(elem):
            return elem


def find_uin_in_giis_list(_id='', _list='', name='', metal='', weight='', art=''):
    counter = 0
    result = None
    if check_id(_id):
        for giis_dict in _list:
            counter += 1
            for giis_key, giis_values in giis_dict.items():
                for item_key, item_value in giis_values.items():
                    if 'ID' in item_key:
                        if _id == giis_values['ID']:
                            result = giis_key
                            return result, counter
                if result:
                    break
            if result:
                break
        if result is None:
            return None, None

    else:
        similar_products = []
        identical_products = []
        for giis_dict in _list:
            counter += 1
            for giis_key, giis_values in giis_dict.items():
                if float(giis_values['Масса'].split(' ')[0]) == weight:
                    if (float(giis_values['Масса'].split(' ')[0]) == weight and name in giis_values['Описание']
                            and metal in giis_values['Описание']):
                        if 'Артикул' in giis_values:
                            if art == giis_values['Артикул']:
                                identical_products.append(giis_dict)
                        else:
                            similar_products.append(giis_dict)
        if len(identical_products) > 0:
            return identical_products
        else:
            return similar_products


def find_uin_in_string(description):
    split_string = description.split(' ')
    for element in split_string:
        if ',' in element:
            element = element.replace(',', '')
        if len(element) == 16 and isinteger(element):
            return element


def find_weight(split_string):
    """ Функция поиска массы(вес) изделия, перебирает элементы, проверяет их на причастность к числу.
    Возвращает вещественное число или None"""

    original_string = ' '.join(split_string)

    if 'вес' in split_string:
        weight_ind = split_string.index('вес') + 1
        split_string = [split_string[weight_ind]]

    elif '—' in split_string or '---' in split_string:
        index = split_string.index('—') if '—' in split_string else split_string.index('---')
        split_string = split_string[index + 1:]

    elif '585' in split_string or '925' in split_string:
        index = split_string.index('585') if '585' in split_string else split_string.index('925')
        split_string = split_string[index + 1:]

    for elem in split_string:
        elem = elem.strip()
        try:
            while not elem[-1].isdigit():
                elem = elem[:-1]
        except IndexError:
            pass

        if ',' in elem:
            elem = elem.replace(',', '.')
        # if elem in sizes:
        #     print(f'Вес изделия, который определила программа, есть в списке размеров изделий. '
        #           f'Вы вы уверены что значение {elem}, находящееся в строке ({original_string}),'
        #           f'действительно является весом изделия?')
        #     answer = input('введите "да", или укажите правильный вес изделия: ')
        #     if answer == 'да':
        #         pass
        #     else:
        #         elem = answer
        if isinteger(elem):
            elem = elem + '.00'
        if isfloat(elem):
            if len(elem.split('.')[1]) == 1:
                elem = elem + '0'
        if check_weight(elem):
            return elem

    else:
        print(f'Программе не удалось определить вес изделия в строке {original_string}')
        answer = ''
        while not check_weight(answer):
            answer = input('Укажите вес изделия в формате 0.00: ')
        return answer


def find_art(*args, group):
    """ Функция анализирует столбцы Описание и Наименование, находит и проверяет артикул позиции
      Возвращает артикул или None. """

    prefixes = ['НЦ', 'ЦБ', 'ЦИ', 'ББ', 'БВ', 'БИ', 'БК', 'НБ', 'шн2/5т']

    for string_from_args in args:

        string_from_args = str(string_from_args).lower().split(' ')

        if 'арт.' in string_from_args:
            art_ind = string_from_args.index('арт.') + 1
            return string_from_args[art_ind].upper()

        if group == 'word':
            if '585'in string_from_args or '925' in string_from_args:
                ind_1 = (string_from_args.index('585') if '585' in string_from_args and 'золото' in string_from_args
                         else string_from_args.index('925'))
                string_from_args = string_from_args[ind_1 + 1:]

                if '—' in string_from_args or '---' in string_from_args:
                    ind_2 = (string_from_args.index('—') if '—' in string_from_args else string_from_args.index('---'))
                    art = string_from_args[: ind_2]
                    return ' '.join(art).upper()

        for elem in string_from_args:
            if len(elem) > 1:
                if elem[-1] == ',':
                    elem = elem[:-1]
            for pref in prefixes:
                if pref in elem:
                    return elem.upper()

            if elem.endswith('перлина') and group == 'excel':
                return elem.replace('перлина', '').upper()

            if ((elem.isdigit() and len(elem) > 3 or elem.isalnum() and not elem.isdigit()) and 2 < len(elem) != 13 and
                    not elem.isalpha() and check_word_exceptions(elem.lower())):
                return elem.upper()

            if ('-' in elem or '_' in elem) and check_word_exceptions(elem) and len(elem) > 3:
                return elem.upper()


def find_name(split_string):
    """ Метод поиска наименования изделия, сопоставляет содержимое строки со списком вариантов имен.
    Возвращает имя или None ."""
    for name in keywords_name:

        if name in split_string:
            return name.capitalize()

    for keywords_key, keywords_values in keywords.items():
        for value in keywords_values:
            if value in split_string:
                return keywords_key.capitalize()


def find_metal(split_string):
    """ Метод определяющий из какого металла изготовлено изделие.
    Возвращает Название металла с пробой или None. """
    if split_string:
        if '585' in split_string or 'золото' in split_string:
            return 'Золото 585'
        elif '925' in split_string or 'серебро' in split_string:
            return 'Серебро 925'
    else:
        return 'unknown'


def find_weaving(split_string):
    """ Метод определяющий плетения для цепей и браслетов, сопоставляет содержимое строки со списком вариантов.
    Возвращает название плетения или None. """

    for keywords_weaving_key, keywords_weaving_values in keywords_weaving.items():
        for value in keywords_weaving_values:
            for elem in split_string:
                if value in elem:
                    return keywords_weaving_key


def find_inserts(split_string):
    """ Метод определяющий вставки в изделия, сопоставляет содержимое строки со списком вариантов.
    Возвращает название плетения или None. """

    for keywords_inserts_key, keywords_inserts_values in keywords_inserts.items():
        for value in keywords_inserts_values:
            if value in split_string:
                return keywords_inserts_key


def find_size(split_string, group):
    """ Метод определяющий размер изделия, перебирает елементы строки, проверяет их на причастность к числам и
    сопоставляет с возможными вариантами размеров.
     Возвращает вещественное число или None. """

    if group == 'excel':
        _string = ''
        if 'размер:' in split_string:
            size_index = split_string.index('размер:') + 1
            _string = split_string[size_index]
        if 'разм.' in split_string or 'разм' in split_string:
            size_index = split_string.index('разм.') + 1 if 'разм.' in split_string else split_string.index('разм') + 1
            _string = split_string[size_index]
        if 'р-р' in split_string:
            size_index = split_string.index('р-р') - 1
            _string = split_string[size_index]
        if 'безразмер.' in _string:
            return 'безразм'
        if ',' in _string:
            _string = _string.replace(',', '.')
        for size in sizes:
            probable_size = _string.find(size)
            if probable_size != -1:
                return size
        else:
            for size in sizes:
                size = str(int(float(size)))
                probable_size = _string.find(size)
                if probable_size != -1:
                    return size + '.0'
        for _string in split_string:
            if _string.startswith('l-'):
                return _string[2:4] + '.0'
            if ' р-р' in _string:
                _string = _string.replace(' р-р', '')
                if ' ' in _string:
                    _string = _string.replace(' ', '')
                if ',' in _string:
                    _string = _string.replace(',', '.')
                if isfloat(_string) and _string in sizes:
                    return _string

    elif group == 'word':

        if '—' in split_string or '---' in split_string:
            index = (split_string.index('—') if '—' in split_string else split_string.index('---'))
            split_string = ((' '.join(split_string).split(split_string[index])[1]).split(' '))[1:]

        for el_r_part in split_string[-1::-1]:
            if len(el_r_part) > 1:
                if ',' in el_r_part:
                    el_r_part.replace(',', '.')
                if isfloat(el_r_part) and el_r_part in sizes:
                    return el_r_part
                if isinteger(el_r_part) and str(float(el_r_part)) in sizes:
                    return str(float(el_r_part))


def find_description(*args, group):
    """ Функция анализирует столбцы Описание, Наименование и Основной металл, находит и составляет описание
        позиции.
        Возвращает описание позиции. """

    # Инструкция для функции "find_description"
    if group == 'word':

        arg = args[0]
        description = f'{find_name(arg)}, {find_metal(arg)}'

        # Определение вставок
        inserts = find_inserts(arg)

        # Определение размера для колец, цепей и браслетов
        size = find_size(arg, group) if (description.split(','))[0] in ('Кольцо', 'Цепь', 'Браслет', 'Колье') else None

        # Определение плетения для цепей и браслетов
        weaving = find_weaving(arg) if (description.split(','))[0] in ['Цепь', 'Браслет'] else None

        if inserts:
            description = f'{description}, c {inserts}'

        if weaving:
            description = f'{description}, плетение - {weaving}'

        if size:
            description = f'{description}, {size} р-р'

        return description

    if group == 'excel':
        _name = metal = weaving = size = inserts = None

        for arg in args:
            split_arg = str(arg).lower().split(' ')
            if not _name:
                _name = find_name(split_arg)
            if not metal:
                metal = find_metal(args[-1])
            if not weaving:
                weaving = find_weaving(split_arg)
            if not size:
                size = find_size(split_arg, group)
            if not inserts:
                inserts = find_inserts(split_arg)

        description = f'{_name}, {metal}'

        if inserts:
            description = f'{description}, c {inserts}'
        if weaving:
            description = f'{description}, плетение - {weaving}'
        if size:
            description = f'{description}, {size} р-р'

        return description

# Test

# print(find_weight('Серьги Серебро 925 0044с-001VMз — 17,5, Кристалл Swarowsky'.split(' ')))


# print(find_size('Цепь, Золото 585, плетение - перлина, 45.0 р-р'.split(','), group='excel'))
