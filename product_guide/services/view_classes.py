import os
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import media
import tempfile
from jewelry_store_management.settings import BASE_DIR
from product_guide.forms.product_guide.forms import UploadFileForm
from product_guide.models import Jewelry, File, Counterparties, Recipient, OutgoingInvoice, IncomingInvoice, Provider
from product_guide.services.anover_functions import make_product_dict_from_dbqueryset
from product_guide.services.file_handling_classes import FileHandler
from product_guide.services.request_classes import Request, Context, clear_media_folder
from product_guide.services.upload_file_methods import file_processing
from product_guide.services.validity import check_uin


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

        if 'file' in request.FILES.keys():
            print('Has a File')
            self.session_cleanup()
            if self.check_and_save_form():
                self.file_path = f'{BASE_DIR}/media/product_guide/documents/{self.file_name}'
                self.page_num = None
                self.file_handler_obj = FileHandler(self)
                self.numbers_of_items_per_page = self.file_handler_obj.numbers_of_items_per_page
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


class SaveProductPropertiesPost(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.context = self.get_context_from_session()
        self.products_dicts_dict = self.get_products_dicts_dict_from_session()
        self.context_changing()
        self.product_dict_changing()
        self.save_context_in_session()

    def context_changing(self):
        properties_dict = self.context['product_list'][int(self.request.POST.get('number')) - 1]
        for key in properties_dict.keys():
            properties_dict[key] = self.request.POST.get(key)

    def product_dict_changing(self):
        product_dict = self.products_dicts_dict[self.request.POST.get('number')]
        for key in product_dict.keys():
            product_dict[key] = self.request.POST.get(key)


class SaveIncomingInvoiceGet(Request):
    def __init__(self, request):
        self.printCreateObject()
        self.request = request
        self.products_dicts_dict_from_session = self.get_products_dicts_dict_from_session()
        self.invoice_requisites = self.get_invoice_requisites_from_session()
        self.context = self.get_context_from_session()
        self.all_products_from_db = Jewelry.get_all_obj()
        self.invoice_id = self.get_or_create_invoice_obj()
        self.products_properties_saving()

    def products_properties_saving(self):
        sinonims_dict = {'invoice_date': 'arrival_date', 'price': 'purchase_price', 'price_per_gram': 'purchase_price_per_gram'}

        def save_properties(product_obj, properties):
            for key, value in properties.items():
                if key in sinonims_dict.keys():
                    key = sinonims_dict[key]
                print('key = ', key, ',', 'value = ', value)
                if key in product_obj.__dict__.keys():
                    product_obj.__setattr__(key, value)
            return product_obj

        for product in self.products_dicts_dict_from_session.values():
            if product['uin'] and check_uin(product['uin']) and len(
                    self.all_products_from_db.filter(uin=product['uin'])) > 0:
                product_obj = Jewelry.get_object('uin', product['uin'])
            else:
                product_obj = Jewelry()

            product_obj = save_properties(product_obj, product)
            product_obj = save_properties(product_obj, self.invoice_requisites)
            product_obj.input_invoice = IncomingInvoice.get_object('id', self.invoice_id)

            product_obj.save()

    def get_or_create_invoice_obj(self):

        def create_title(requisites_dict):
            provider_obj = Provider.get_object('id', requisites_dict['provider_id'])
            provider_surname = provider_obj.title
            invoice_number = requisites_dict['invoice_number']
            arrival_date = requisites_dict['invoice_date']

            return f'Входящая накладная № {invoice_number} от {provider_surname} {arrival_date}'

        invoice_queryset = IncomingInvoice.get_all_obj().filter(invoice_number=self.invoice_requisites['invoice_number'],
                                                                provider_id=self.invoice_requisites['provider_id'],
                                                                arrival_date=self.invoice_requisites['invoice_date'])
        if len(invoice_queryset) == 1:
            invoice_obj = invoice_queryset[0]
        else:
            invoice_obj = IncomingInvoice()
            invoice_obj.title = create_title(self.invoice_requisites)
            invoice_obj.invoice_number = self.invoice_requisites['invoice_number']
            invoice_obj.provider = Provider.get_object('id', self.invoice_requisites['provider_id'])
            invoice_obj.arrival_date = self.invoice_requisites['invoice_date']
            invoice_obj.save()

        return invoice_obj.id
