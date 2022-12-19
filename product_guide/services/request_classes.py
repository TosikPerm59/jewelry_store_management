import traceback
import os
from django.core.paginator import Paginator
from django.shortcuts import render

from jewelry_store_management.settings import BASE_DIR
from product_guide.models import Counterparties, Recipient, Provider
from product_guide.services.anover_functions import make_product_queryset_from_dict_dicts, \
    find_products_in_db, has_filters_check, make_product_dict_from_dbqueryset, \
    search_query_processing
from product_guide.services.validity import isfloat, isinteger


class RequestSession:
    """ Класс для работы с сессией. """

    def session_cleanup(self):
        print('Очистка данных из сессии')
        self.delete_filtered_list_from_session()
        self.delete_products_dicts_dict_from_session()
        self.delete_invoice_requisites_from_session()
        self.delete_context_from_session()
        self.delete_template_path_from_session()

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
        if 'products_objects_dict_for_view' in self.request.session.keys():
            print('Удаление словаря словарей продуктов из сессии')
            self.request.session.pop('products_objects_dict_for_view')

    def save_invoice_requisites_in_session(self):
        print('Сохранение данных накладной в сессии')
        self.request.session['invoice_requisites'] = self.invoice_requisites

    def get_invoice_requisites_from_session(self):
        print('Получение данных накладной из сессии')
        return self.request.session['invoice_requisites']

    def delete_invoice_requisites_from_session(self):
        if 'invoice_requisites' in self.request.session.keys():
            print('Удаление данных накладной из сессии')
            self.request.session.pop('invoice_requisites')

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

    def save_template_path_in_session(self):
        print('Сохранение контекста в сессии')
        self.request.session['template_path'] = self.template_path

    def get_template_path_from_session(self):
        print('Получение контекста из сессии')
        return self.request.session['template_path']

    def delete_template_path_from_session(self):
        if 'template_path' in self.request.session.keys():
            print('Удаление template_path из сессии')
            self.request.session.pop('template_path')


class Request(RequestSession):

    @staticmethod
    def set_correct_file_name(file_name):
        for simbol in [' ', '№']:
            file_name = file_name.replace(simbol, '_') if simbol in file_name else file_name
            file_name = file_name.replace('(', '') if '(' in file_name else file_name
            file_name = file_name.replace(')', '') if ')' in file_name else file_name
            file_name = file_name.replace('__', '_') if '__' in file_name else file_name
        return file_name

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

    def printCreateObject(self):
        """ Выводит сообщение о создании нового обьекта, относящегося к классу. """

        print()
        print(f'Create {self.__class__.__name__} object')
        print()

    def get_attr_from_POST(self, attr):
        return self.request.POST.get(attr)

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
        print('Выполняется получение фильтров')
        self.search_string = self.get_attr_from_POST('search_string')
        if self.search_string:
            print('search_string = ', self.search_string)
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

    def show_exception(self, exception_text):
        splitted_exception_text = exception_text.split('\n')
        context = {'exception_list': splitted_exception_text}
        return render(self.request_obj.request, 'product_guide/show_exception.html', context=context)


class Context:

    def __init__(self, request_obj):
        self.request_obj = request_obj
        self.products_dicts_dict = request_obj.products_dicts_dict
        self.total_weight = self.calculate_total_weight()
        self.number_of_products = len(self.products_dicts_dict.keys())
        if self.number_of_products > 0:
            product_queryset = make_product_queryset_from_dict_dicts(self.products_dicts_dict)
            self.paginator_obj = Paginator(product_queryset, request_obj.numbers_of_items_per_page)
            self.page = self.paginator_obj.get_page(request_obj.page_num)
            self.context = self.get_default_context()
            if request_obj.__class__.__name__ == 'UploadFilePost':
                self.set_context_for_UploadFilePost()
            return
        self.context = None

    @staticmethod
    def get_context(request_obj):
        context_obj = Context(request_obj)
        return context_obj.context

    def calculate_total_weight(self):
        total_weight = 0
        try:
            for product in self.products_dicts_dict.values():
                if isfloat(product['weight']):
                    total_weight += float(product['weight'])
            return total_weight
        except Exception:
            return self.request_obj.show_exception(traceback.format_exc())

    def get_default_context(self):
        return {
                'product_list': self.page.object_list,
                'position_list': [x + 1 for x in range(self.number_of_products)],  # Список номеров позиций
                'num_pages': [x for x in range(self.paginator_obj.num_pages + 1)][1:],  # Список номеров страниц
                'total_weight': round(self.total_weight, ndigits=2) if self.total_weight else '',  # Общий вес изделий в списке
                'len_products': self.number_of_products  # Количество изделий в списке
            }

    def set_context_for_UploadFilePost(self):
        print('Добавление данных в контекст UploadFilePost')
        invoice_requisites = self.request_obj.get_invoice_requisites_from_session()
        self.context['invoice_title'] = invoice_requisites['title']

        if self.request_obj.invoice_requisites['invoice_type'] != 'giis_report':
            self.context['recipient_surname'] = Recipient.get_object('id', invoice_requisites['recipient_id']).counterparties.surname
            self.context['invoice_date'] = invoice_requisites['invoice_date']
            self.context['invoice_number'] = invoice_requisites['invoice_number']
            self.context['provider_surname'] = Provider.get_object('id', invoice_requisites['provider_id']).counterparties.surname

        if invoice_requisites['invoice_type'] == 'incoming_invoice':
            print('Добавление prod_list в контекст')
            self.context['prod_list'] = find_products_in_db(self.products_dicts_dict)


def clear_media_folder():
    print('Run clear_media_folder')
    folder = f'{BASE_DIR}\media\product_guide\documents'
    for files in os.walk(folder):
        for name in files[2]:
            path = f'{folder}\\{name}'
            os.remove(path)



