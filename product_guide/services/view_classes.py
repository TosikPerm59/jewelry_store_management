from django.utils.datastructures import MultiValueDictKeyError

from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.services.anover_functions import search_query_processing, has_filters_check, \
    make_product_queryset_from_dict_dicts, make_product_dict_from_dbqueryset
from product_guide.services.upload_file_methods import set_correct_file_name, save_form, file_processing
from product_guide.services.validity import isfloat, isinteger


class Request:
    pass


class RequestSession(Request):

    @staticmethod
    def session_cleanup(request):
        RequestSession.delete_filtered_list_from_session(request)
        RequestSession.delete_products_dicts_dict_from_session(request)
        RequestSession.delete_invoice_data_from_session(request)

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


class RequestPost(Request):
    @staticmethod
    def get_attr_from_POST(request, attr):
        return request.POST.get(attr)


class ShowProductsPost(RequestPost):
    def __init__(self, request):
        print('create RequestPost object')
        self.page_num = ShowProductsPost.get_page_num(request)
        if self.page_num:
            print('PAGE_NUM = ', self.page_num)
            if 'filtered_list' in request.session.keys():
                self.product_dicts_dict = RequestSession.get_filtered_list_from_session(request)
        else:
            print('PAGE_NUM is None')
            self.search_string = ShowProductsPost.get_search_string(request)
            if self.search_string:
                print('Request has SearchString')
                self.filters_dict = search_query_processing(self.search_string)
            else:
                print('Request not have SearchString')
                self.filters_dict = ShowProductsPost.create_filters_dict(request)

            self.product_dicts_dict = RequestSession.get_product_dicts_dict_from_session(request)
            if has_filters_check(self.filters_dict) is False:
                print('Request not have FILTERS')
                RequestSession.delete_filtered_list_from_session(request)
            else:
                print('Request has FILTERS')
                product_list = make_product_queryset_from_dict_dicts(self.product_dicts_dict)
                for key, value in self.filters_dict.items():
                    if value != 'all':
                        value = float(value) if isfloat(value) else value
                        value = int(value) if isinteger(value) else value
                        product_list = [p for p in product_list if p[key] == value]
                self.product_dicts_dict = make_product_dict_from_dbqueryset(product_list)
                RequestSession.save_filtered_list_in_session(request, self.product_dicts_dict)

    @staticmethod
    def create_filters_dict(request, ):
        filters_dict = {
            'name': request.POST.get('name') if request.POST.get('name') else 'all',
            'metal': request.POST.get('metal') if request.POST.get('metal') else 'all',
            'availability_status': request.POST.get('availability_status') if request.POST.get(
                'availability_status') else 'all',
            'giis_status': request.POST.get('giis_status') if request.POST.get('giis_status') else 'all'
        }
        return filters_dict

    @staticmethod
    def get_page_num(request):
        return request.POST.get('page')

    @staticmethod
    def get_search_string(request):
        return request.POST.get('search_string')


class UploadFilePost(RequestPost):
    def __init__(self, request):
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
        except MultiValueDictKeyError:
            print('EXCEPTIONS')
            pass


class Save_Incoming_Invoice():
    pass

