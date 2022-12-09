from django.core.paginator import Paginator
from product_guide.models import Counterparties
from product_guide.services.anover_functions import calculate_weight_number_price, \
    make_product_queryset_from_dict_dicts, find_products_in_db, has_filters_check, make_product_dict_from_dbqueryset, \
    search_query_processing
from product_guide.services.validity import isfloat, isinteger


class RequestSession:
    """ Класс для работы с сессией. """

    def session_cleanup(self):
        self.delete_filtered_list_from_session()
        self.delete_products_dicts_dict_from_session()
        self.delete_invoice_data_from_session()
        self.delete_context_from_session()

    def save_filtered_list_in_session(self):
        print('Сохранение отфильтрованного списка продуктов в сессии')
        self.request.session['filtered_list'] = self.products_dicts_dict

    def get_filtered_list_from_session(self):
        print('Получение отфильтрованного списка продуктов из сессии')
        return self.request.session['filtered_list']

    def delete_filtered_list_from_session(self):
        if 'filtered_list' in self.request.session.keys():
            print('Удаление отфильтрованного списка продуктов из сессии')
            self.request.session.pop('filtered_list')

    def save_products_dicts_dict_in_session(self):
        print('Сохранение словаря словарей продуктов в сессии')
        self.request.session['products_objects_dict_for_view'] = self.products_dicts_dict

    def get_products_dicts_dict_from_session(self):
        print('Получение словаря словарей продуктов из сессии')
        return self.request.session['products_objects_dict_for_view']

    def delete_products_dicts_dict_from_session(self):
        if 'product_objects_dict_for_view' in self.request.session.keys():
            print('Удаление словаря словарей продуктов из сессии')
            self.request.session.pop('products_objects_dict_for_view')

    def save_invoice_data_in_session(self):
        print('Сохранение данных накладной в сессии')
        self.request.session['invoice'] = self.invoice_data

    def get_invoice_data_from_session(self):
        print('Получение данных накладной из сессии')
        return self.request.session['invoice']

    def delete_invoice_data_from_session(self):
        if 'invoice' in self.request.session.keys():
            print('Удаление данных накладной из сессии')
            self.request.session.pop('invoice')

    def save_context_in_session(self):
        print('Сохранение контекста в сессии')
        self.request.session['context'] = self.context

    def get_context_from_session(self):
        print('Получение контекста из сессии')
        return self.request.session['context']

    def delete_context_from_session(self):
        if 'context' in self.request.session.keys():
            print('Удаление контекста из сессии')
            self.request.session.pop('context')


class Request(RequestSession):

    def printCreateObject(self):
        """ Выводит сообщение о создании нового обьекта, относящегося к классу. """

        print()
        print(f'Create {self.__class__.__name__} object')

    def get_attr_from_POST(self, attr):
        return self.request.POST.get(attr)

    def get_context(self):
        print('Getting context')
        # Определение общего веса и количества изделий из products_dicts_dict
        total_weight, number_of_products = calculate_weight_number_price(self.products_dicts_dict)
        # Конвертация dict в list
        product_queryset = make_product_queryset_from_dict_dicts(self.products_dicts_dict)
        # Разбиение всех изделий из products_dicts_dict постранично по 15 штук
        paginator = Paginator(product_queryset, self.numbers_of_products_per_page)
        # Получение списка изделий для выбранной пользователем страницы
        page = paginator.get_page(self.page_num)
        # Создание dict с контекстом
        context = {
            'product_list': page.object_list,
            'position_list': [x + 1 for x in range(number_of_products)],  # Список номеров позиций
            'num_pages': [x for x in range(paginator.num_pages + 1)][1:],  # Список номеров страниц
            'total_weight': round(total_weight, ndigits=2),  # Общий вес изделий в списке
            'len_products': number_of_products  # Количество изделий в списке
        }
        if self.__class__.__name__ == 'UploadFilePost':
            print('Append additional data')
            invoice_data = self.get_invoice_data_from_session()
            context['prod_list'] = find_products_in_db(self.products_dicts_dict)
            context['invoice_title'] = invoice_data['title']
            context['invoice_date'] = invoice_data['arrival_date']
            context['invoice_number'] = invoice_data['invoice_number']
            context['provider_surname'] = Counterparties.get_object('id', invoice_data['provider_id']).surname
        return context

    def get_products_dicts_dict_from_request(self):
        print('Getting product_dicts_dict')
        if self.page_num:
            self.products_dicts_dict = self.get_products_dicts_dict_if_request_has_page_num()
            return

        print('PAGE_NUM is None')
        filters_dict = self.get_filters_dict()
        products_dicts_dict = self.get_products_dicts_dict_from_session()
        if has_filters_check(filters_dict) is False:
            print('Request not have FILTERS')
            self.products_dicts_dict = products_dicts_dict
            self.delete_filtered_list_from_session()
            return

        print('Request has FILTERS')
        self.products_dicts_dict = self.get_filtered_products_dicts_dict(products_dicts_dict, filters_dict)
        self.save_filtered_list_in_session()

    @staticmethod
    def get_filtered_products_dicts_dict(products_dicts_dict, filters_dict):
        product_list = make_product_queryset_from_dict_dicts(products_dicts_dict)
        for key, value in filters_dict.items():
            if value != 'all':
                value = float(value) if isfloat(value) else value
                value = int(value) if isinteger(value) else value
                product_list = [p for p in product_list if key in p.keys() and p[key] == value]
        filtered_products_dicts_dict = make_product_dict_from_dbqueryset(product_list)
        return filtered_products_dicts_dict

    def get_products_dicts_dict_or_filtered_list_from_session(self):
        """ Функция получения словаря словарей продуктов из сессии. Возвращает
        filtered list, если он есть в сессии или products_dicts_dict из сессии"""
        if 'filtered_list' in self.request.session.keys():
            print('Request has filtered list')
            product_dicts_dict = self.get_filtered_list_from_session()
            return product_dicts_dict
        print('Request not have filtered list')
        products_dicts_dict = self.get_products_dicts_dict_from_session()
        return products_dicts_dict

    def get_filters_dict(self):
        self.search_string = self.get_attr_from_POST('search_string')
        if self.search_string:
            print('Request has SearchString')
            filters_dict = search_query_processing(self.search_string)
            return filters_dict
        print('Request not have SearchString')
        filters_dict = self.create_filters_dict()
        return filters_dict

    def get_products_dicts_dict_if_request_has_page_num(self):
        print('PAGE_NUM = ', self.page_num)
        products_dicts_dict = self.get_products_dicts_dict_or_filtered_list_from_session()
        return products_dicts_dict

    def create_filters_dict(self):
        filters_dict = {}
        for attr in ['name', 'metal', 'availability_status', 'giis_status']:
            filters_dict[attr] = self.get_attr_from_POST(attr) if self.get_attr_from_POST(attr) else 'all'
        return filters_dict

    @staticmethod
    def set_correct_file_name(file_name):
        for simbol in [' ', '№', '(', ')']:
            file_name = file_name.replace(simbol, '_') if simbol in file_name else file_name
        return file_name
