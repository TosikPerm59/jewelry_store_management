from django.core.exceptions import ObjectDoesNotExist
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.models import Jewelry, File
from product_guide.services.anover_functions import make_product_dict_from_dbqueryset
from product_guide.services.request_classes import Request, Context
from product_guide.services.upload_file_methods import file_processing


def createRequestObject(request, func_name):
    get_class = lambda x: globals()[x]
    request_obj = get_class(func_name + request.method.capitalize())(request)
    print(f'Передача данных контроллеру {func_name}')
    print()
    return request_obj


class ShowProductsPost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_items_per_page = 30
        self.page_num = self.get_attr_from_POST('page_num')
        self.get_products_dicts_dict_from_request()
        self.context = Context.get_context(self)


class ShowProductsGet(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_items_per_page = 30
        self.session_cleanup()
        print('Получение словаря словарей продуктов из Jewelry')
        products_dicts_list = Jewelry.get_all_values()
        self.products_dicts_dict = make_product_dict_from_dbqueryset(products_dicts_list)
        self.save_products_dicts_dict_in_session()
        self.page_num = None
        self.context = Context.get_context(self)


class UploadFilePost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_items_per_page = 15

        if 'file' in request.FILES.keys():
            print('Has a File')
            self.session_cleanup()
            if self.check_and_save_form():
                path = 'C:\Python\Python_3.10.4\Django\jewelry_store_management\media\product_guide\documents\\'
                self.page_num = None
                self.context, self.products_dicts_dict, self.invoice_data, self.template_path = \
                    file_processing(self.file_name, path + self.file_name)
                self.save_products_dicts_dict_in_session()
                self.save_invoice_data_in_session()
                self.save_context_in_session()
                return

        print('Not have a File')
        self.page_num = self.get_attr_from_POST('page_num')
        self.get_products_dicts_dict_from_request()
        self.template_path = 'product_guide\show_incoming_invoice.html'
        self.context = Context.get_context(self)

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

