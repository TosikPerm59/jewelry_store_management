from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils.datastructures import MultiValueDictKeyError
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.models import Jewelry, File
from product_guide.services.anover_functions import search_query_processing, has_filters_check, \
    make_product_queryset_from_dict_dicts, make_product_dict_from_dbqueryset, calculate_weight_number_price
from product_guide.services.upload_file_methods import set_correct_file_name, save_form, file_processing
from product_guide.services.validity import isfloat, isinteger


class Print:
    """ Класс вывода сервисных сообщений в консоль. """

    def printCreateObject(self):
        """ Выводит сообщение о создании нового обьекта, относящегося к классу. """
        print()
        print(f'Create {self.__class__.__name__} object')
        print()


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
        request.session['filtered_list'] = product_dicts_dict

    @staticmethod
    def get_filtered_list_from_session(request):
        return request.session['filtered_list']

    @staticmethod
    def delete_filtered_list_from_session(request):
        if 'filtered_list' in request.session.keys():
            request.session.pop('filtered_list')

    @staticmethod
    def save_product_dicts_dict_in_session(request, product_dicts_dict):
        request.session['product_objects_dict_for_view'] = product_dicts_dict

    @staticmethod
    def get_product_dicts_dict_from_session(request):
        return request.session['product_objects_dict_for_view']

    @staticmethod
    def delete_products_dicts_dict_from_session(request):
        if 'product_objects_dict_for_view' in request.session.keys():
            request.session.pop('product_objects_dict_for_view')

    @staticmethod
    def save_invoice_data_in_session(request, invoice_data):
        request.session['invoice'] = invoice_data

    @staticmethod
    def get_invoice_data_from_session(request):
        return request.session['invoice']

    @staticmethod
    def delete_invoice_data_from_session(request):
        if 'invoice' in request.session.keys():
            request.session.pop('invoice')

    @staticmethod
    def save_context_in_session(request, context):
        request.session['context'] = context

    @staticmethod
    def get_context_from_session(request):
        return request.session['context']

    @staticmethod
    def delete_context_from_session(request):
        if 'context' in request.session.keys():
            request.session.pop('context')


class Request:

    @staticmethod
    def createRequestObject(request, func_name):
        get_class = lambda x: globals()[x]
        request_obj = get_class(func_name + request.method.capitalize())(request)
        print(hasattr(request_obj, 'products_dicts_dict'))
        context = request_obj.get_context()
        return context

    def get_attr_from_POST(self, attr):
        return self.request.POST.get(attr)

    def get_context(self):

        # Определение общего веса и количества изделий из products_dicts_dict
        total_weight, number_of_products = calculate_weight_number_price(self.products_dicts_dict)
        # Конвертация dict в list
        product_queryset = make_product_queryset_from_dict_dicts(self.products_dicts_dict)
        product_list = []
        # Разбиение всех изделий из products_dicts_dict постранично по 50 штук
        paginator = Paginator(product_queryset, 50)
        # Получение списка изделий для выбранной пользователем страницы
        page = paginator.get_page(self.page_num)
        # Создание dict с контекстом
        context = {
            'product_list': page.object_list,
            'position_list': [x for x in range(number_of_products)],  # Список номеров позиций
            'num_pages': [x for x in range(paginator.num_pages + 1)][1:],  # Список номеров страниц
            'total_weight': round(total_weight, ndigits=2),  # Общий вес изделий в списке
            'len_products': number_of_products  # Количество изделий в списке
        }
        return context

    def get_products_dicts_dict_from_request(self):
        if self.page_num:

            print('PAGE_NUM = ', self.page_num)
            products_dicts_dict = self.get_products_dicts_dict_from_session()
            return products_dicts_dict

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
                product_list = [p for p in product_list if p[key] == value]
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
        filters_dict = self.create_filters_dict(self.request)
        return filters_dict

    @staticmethod
    def create_filters_dict(request):
        filters_dict = {
            'name': request.POST.get('name') if request.POST.get('name') else 'all',
            'metal': request.POST.get('metal') if request.POST.get('metal') else 'all',
            'availability_status': request.POST.get('availability_status') if request.POST.get(
                'availability_status') else 'all',
            'giis_status': request.POST.get('giis_status') if request.POST.get('giis_status') else 'all'
        }
        return filters_dict


class ShowProductsPost(Request, Print):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.page_num = self.get_attr_from_POST('page_num')
        self.products_dicts_dict = self.get_products_dicts_dict_from_request()


class ShowProductsGet(Request, Print):
    def __init__(self, request):
        self.printCreateObject()
        RequestSession.session_cleanup(request)
        products_dicts_list = Jewelry.get_all_values()
        self.products_dicts_dict = make_product_dict_from_dbqueryset(products_dicts_list)
        RequestSession.save_product_dicts_dict_in_session(request, self.products_dicts_dict)
        self.page_num = None


class UploadFilePost(Request, Print):
    def __init__(self, request):
        self.request = request
        self.printCreateObject()
        page_num = self.get_attr_from_POST('page_num')
        if page_num:
            print('PAGE_NUM = ', page_num)
            request_obj = UploadFileHasPageNum(request, page_num)
            self.products_dicts_dict = request_obj.products_dicts_dict
            self.context = request_obj.context
            self.template_path = request_obj.template_path

        else:
            form = UploadFileForm(request.POST, request.FILES)
            try:
                file = request.FILES['file']
                if file:
                    print('Has a File')
                    self.file_name = set_correct_file_name(file.name)
                    form.title = self.file_name
                    if form.is_valid():
                        print('Form is Valid')
                        save_form(form)
                        path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\'
                        self.file_path = path + self.file_name
                        self.context, self.products_dicts_dict, self.invoice_session_data, self.template_path = \
                            file_processing(self.file_name, self.file_path)
                        RequestSession.save_product_dicts_dict_in_session(request, self.products_dicts_dict)
                        RequestSession.save_invoice_data_in_session(request, self.invoice_session_data)
                        print(self.context)
                        # RequestSession.save_context_in_session(request, self.context)

            except MultiValueDictKeyError:
                print('EXCEPTIONS')
                pass


class UploadFileHasPageNum:
    def __init__(self, request, page_num):

        if 'filtered_list' in request.session.keys():
            print('Request has filtered list')
            self.products_dicts_dict = RequestSession.get_filtered_list_from_session(request)
        else:
            print('Request not have filtered list')
            self.products_dicts_dict = RequestSession.get_product_dicts_dict_from_session(request)
        self.context = RequestSession.get_context_from_session(request)
        self.template_path = 'product_guide\show_incoming_invoice.html'


class CheckAndSaveForm:

    def __init__(self):
        pass

    @staticmethod
    def check_and_save_form(request):
        form = UploadFileForm(request.POST, request.FILES)
        file = request.FILES['file']
        if file:
            print('Has a File')
            file_name = set_correct_file_name(file.name)
            form.title = file_name
            if form.is_valid():
                print('Form is Valid')
                save_form(form)
                path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\'
                file_path = path + file_name

    @staticmethod
    def save_form(form):
        file_object = None
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



