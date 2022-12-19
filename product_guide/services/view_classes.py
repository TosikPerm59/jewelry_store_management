import os
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import media
import tempfile
from jewelry_store_management.settings import BASE_DIR
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.models import Jewelry, File, Counterparties, Recipient, OutgoingInvoice
from product_guide.services.anover_functions import make_product_dict_from_dbqueryset
from product_guide.services.file_handling_classes import FileHandler
from product_guide.services.request_classes import Request, Context, clear_media_folder
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
        products_dicts_list = Jewelry.get_all_values()
        self.products_dicts_dict = make_product_dict_from_dbqueryset(products_dicts_list)
        self.save_products_dicts_dict_in_session()
        self.page_num = None
        self.context = Context.get_context(self)


class UploadFilePost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_items_per_page = 30

        if 'file' in request.FILES.keys():
            print('Has a File')
            self.session_cleanup()
            if self.check_and_save_form():
                self.file_path = f'{BASE_DIR}/media/product_guide/documents/{self.file_name}'
                self.page_num = None
                self.file_handler_obj = FileHandler(self)
                self.products_dicts_dict = self.file_handler_obj.products_dicts_dict
                self.invoice_requisites = self.file_handler_obj.invoice_requisites
                self.invoice_requisites['title'] = self.file_name
                self.save_template_path_in_session()
                self.save_products_dicts_dict_in_session()
                self.save_invoice_requisites_in_session()
                self.context = Context.get_context(self)
                self.save_context_in_session()
                clear_media_folder()
                return

        print('Not have a File')
        self.page_num = self.get_attr_from_POST('page_num')
        self.get_products_dicts_dict_from_request()
        self.template_path = self.get_template_path_from_session()
        self.context = Context.get_context(self)

    def check_and_save_form(self):
        file = self.request.FILES['file']
        self.file_name = self.set_correct_file_name(file.name)
        form = UploadFileForm(self.request.POST, self.request.FILES)
        form.title = self.file_name
        if form.is_valid():
            print('Form is Valid')
            self.save_form(form)
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
        print('Файл сохранен успешно')


class SaveChangesGet(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.numbers_of_items_per_page = 30
        self.page_num = None
        self.products_dicts_dict = self.get_products_dicts_dict_from_session()
        invoice_requisites = self.get_invoice_requisites_from_session()
        recipient_id = invoice_requisites['recipient_id']
        products_dicts_queryset = []
        for key, product in self.products_dicts_dict.items():
            product_obj = Jewelry.find_product(product)
            if product_obj:
                product_obj.availability_status = 'Передано'
                product_obj.recipient = Recipient.get_object('id', recipient_id)
                product_obj.selling_price = product['price']
                product_obj.departure_date = invoice_requisites['invoice_date']
                product_obj.outgoing_invoice = OutgoingInvoice.get_object('title', invoice_requisites['title'])
                product_obj.save()
                products_dicts_queryset.append(product_obj.__dict__)
                self.products_dicts_dict = make_product_dict_from_dbqueryset(products_dicts_queryset)

        self.context = Context.get_context(self)




