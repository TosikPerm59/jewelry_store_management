from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.models import Jewelry, File, Counterparties
from product_guide.services.anover_functions import search_query_processing, has_filters_check, \
    make_product_queryset_from_dict_dicts, make_product_dict_from_dbqueryset, calculate_weight_number_price, \
    find_products_in_db
from product_guide.services.upload_file_methods import set_correct_file_name, save_form, file_processing
from product_guide.services.validity import isfloat, isinteger


class Print:
    """ Класс вывода сервисных сообщений в консоль. """

    def printCreateObject(self):
        """ Выводит сообщение о создании нового обьекта, относящегося к классу. """

        print()
        print(f'Create {self.__class__.__name__} object')


class RequestSession:
    """ Класс для работы с сессией. """

    @staticmethod
    def session_cleanup(request):
        RequestSession.delete_filtered_list_from_session(request)
        RequestSession.delete_products_dicts_dict_from_session(request)
        RequestSession.delete_invoice_data_from_session(request)
        RequestSession.delete_context_from_session(request)

    @staticmethod
    def save_filtered_list_in_session(request, product_dicts_dict):
        print('Сохранение отфильтрованного списка продуктов в сессии')
        request.session['filtered_list'] = product_dicts_dict

    @staticmethod
    def get_filtered_list_from_session(request):
        print('Получение отфильтрованного списка продуктов из сессии')
        return request.session['filtered_list']

    @staticmethod
    def delete_filtered_list_from_session(request):
        if 'filtered_list' in request.session.keys():
            print('Удаление отфильтрованного списка продуктов из сессии')
            request.session.pop('filtered_list')

    @staticmethod
    def save_product_dicts_dict_in_session(request, product_dicts_dict):
        print('Сохранение словаря словарей продуктов в сессии')
        request.session['product_objects_dict_for_view'] = product_dicts_dict

    @staticmethod
    def get_product_dicts_dict_from_session(request):
        print('Получение словаря словарей продуктов из сессии')
        return request.session['product_objects_dict_for_view']

    @staticmethod
    def delete_products_dicts_dict_from_session(request):
        if 'product_objects_dict_for_view' in request.session.keys():
            print('Удаление словаря словарей продуктов из сессии')
            request.session.pop('product_objects_dict_for_view')

    @staticmethod
    def save_invoice_data_in_session(request, invoice_data):
        print('Сохранение данных накладной в сессии')
        request.session['invoice'] = invoice_data

    @staticmethod
    def get_invoice_data_from_session(request):
        print('Получение данных накладной из сессии')
        return request.session['invoice']

    @staticmethod
    def delete_invoice_data_from_session(request):
        if 'invoice' in request.session.keys():
            print('Удаление данных накладной из сессии')
            request.session.pop('invoice')

    @staticmethod
    def save_context_in_session(request, context):
        print('Сохранение контекста в сессии')
        request.session['context'] = context

    @staticmethod
    def get_context_from_session(request):
        print('Получение контекста из сессии')
        return request.session['context']

    @staticmethod
    def delete_context_from_session(request):
        if 'context' in request.session.keys():
            print('Удаление контекста из сессии')
            request.session.pop('context')


class Request(Print):

    @staticmethod
    def createRequestObject(request, func_name):
        get_class = lambda x: globals()[x]
        request_obj = get_class(func_name + request.method.capitalize())(request)
        print(f'Передача данных контроллеру {func_name}')
        print()
        return request_obj

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
            invoice_data = RequestSession.get_invoice_data_from_session(self.request)
            context['prod_list'] = find_products_in_db(self.products_dicts_dict)
            print('find_products_in_db = ', context['prod_list'])
            context['invoice_title'] = invoice_data['title']
            context['invoice_date'] = invoice_data['arrival_date']
            context['invoice_number'] = invoice_data['invoice_number']
            context['provider_surname'] = Counterparties.get_object('id', invoice_data['provider_id']).surname
        return context

    def get_products_dicts_dict_from_request(self):
        print('Getting product_dicts_dict')
        if self.page_num:
            return self.get_products_dicts_dict_if_request_has_page_num()

        print('PAGE_NUM is None')
        filters_dict = self.get_filters_dict()
        products_dicts_dict = RequestSession.get_product_dicts_dict_from_session(self.request)
        if has_filters_check(filters_dict) is False:
            print('Request not have FILTERS')
            RequestSession.delete_filtered_list_from_session(self.request)
            return products_dicts_dict

        print('Request has FILTERS')
        products_dicts_dict = self.get_filtered_products_dicts_dict(products_dicts_dict, filters_dict)
        RequestSession.save_filtered_list_in_session(self.request, products_dicts_dict)
        return products_dicts_dict

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

    def get_products_dicts_dict_from_session(self):
        """ Функция получения словаря словарей продуктов из сессии. Возвращает
        filtered list, если он есть в сессии или products_dicts_dict из сессии"""
        if 'filtered_list' in self.request.session.keys():
            print('Request has filtered list')
            product_dicts_dict = RequestSession.get_filtered_list_from_session(self.request)
            return product_dicts_dict
        print('Request not have filtered list')
        products_dicts_dict = RequestSession.get_product_dicts_dict_from_session(self.request)
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
        products_dicts_dict = self.get_products_dicts_dict_from_session()
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


class ShowProductsPost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_products_per_page = 50
        self.page_num = self.get_attr_from_POST('page_num')
        self.products_dicts_dict = self.get_products_dicts_dict_from_request()
        self.context = self.get_context()


class ShowProductsGet(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.numbers_of_products_per_page = 50
        RequestSession.session_cleanup(request)
        print('Получение словаря словарей продуктов из Jewelry')
        products_dicts_list = Jewelry.get_all_values()
        self.products_dicts_dict = make_product_dict_from_dbqueryset(products_dicts_list)
        RequestSession.save_product_dicts_dict_in_session(request, self.products_dicts_dict)
        self.page_num = None
        self.context = self.get_context()


class UploadFilePost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_products_per_page = 20

        if 'file' in request.FILES.keys():
            print('Has a File')
            if self.check_and_save_form():
                path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\'
                self.page_num = None
                self.context, self.products_dicts_dict, self.invoice_session_data, self.template_path = \
                    file_processing(self.file_name, path + self.file_name)
                RequestSession.save_product_dicts_dict_in_session(request, self.products_dicts_dict)
                RequestSession.save_invoice_data_in_session(request, self.invoice_session_data)
                RequestSession.save_context_in_session(self.request, self.context)
                return

        print('Not have a File')
        self.page_num = self.get_attr_from_POST('page_num')
        self.products_dicts_dict = self.get_products_dicts_dict_from_request()
        self.template_path = 'product_guide\show_incoming_invoice.html'
        self.context = self.get_context()

    def check_and_save_form(self):
        file = self.request.FILES['file']
        self.file_name = self.set_correct_file_name(file.name)
        form = UploadFileForm(self.request.POST, self.request.FILES)
        form.title = self.file_name
        if form.is_valid():
            print('Form is Valid')
            save_form(form)
            return True

    @staticmethod
    def save_form(form):
        try:
            file_object = File.get_object('title', form.title)
            if file_object:
                file_object.delete()
        except ObjectDoesNotExist:
            pass
        form.save()
        file_object = File.objects.latest('id')
        file_object.title = form.title
        file_object.save()

