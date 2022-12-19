import os
from product_guide.models import OutgoingInvoice, Jewelry, Manufacturer, Recipient, Provider
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.invoice_parser import word_invoice_parsing
from product_guide.services.parsers_classes import GiisReportParser
from product_guide.services.readers_classes import ReadExcelFile, ReadWordFile
from product_guide.services.request_classes import Request


class FileHandler:
    def __init__(self, request_obj):
        Request.printCreateObject(self)
        self.request_obj = request_obj
        self.file_name = request_obj.file_name
        self.file_path = request_obj.file_path
        self.file_extension = self.file_name.split('.')[1]
        self.file_data_obj = self.extract_data_from_file()
        self.products_dicts_dict = self.parsing_data_object()


    def extract_data_from_file(self):
        """Определение типа файла.
            Возвращает строку 'msexcel' или 'msword'."""

        if self.file_extension == 'xls' or self.file_extension == 'xlsx':
            return ReadExcelFile(self)
        elif self.file_extension == 'doc' or self.file_extension == 'docx':
            return ReadWordFile(self)

    def parsing_data_object(self):
        if self.file_extension == 'xlsx':

            if self.request_obj.file_name.startswith('4_BATCH_LIST_PRINT'):
                self.invoice_requisites['invoice_type'] = 'giis_report'
                self.request_obj.template_path = 'product_guide/show_giis_report.html'
                return GiisReportParser(self).products_dicts_dict

        elif self.file_extension == 'docx':
            products_dicts_dict, self.invoice_requisites = word_invoice_parsing(self.file_data_obj.header_table, self.file_data_obj.product_table)
            provider_id = self.invoice_requisites['provider_id']
            provider_obj = Provider.get_object('id', provider_id)
            if provider_obj.counterparties.surname == 'Александрова':
                self.save_outgoing_invoice_object()
                self.invoice_requisites['invoice_type'] = 'outgoing_invoice'
                self.request_obj.template_path = 'product_guide/show_outgoing_invoice.html'
                return products_dicts_dict

    def save_outgoing_invoice_object(self):
        if self.file_name in OutgoingInvoice.get_all_values_list('title'):
            return

        invoice_object = OutgoingInvoice()
        invoice_object.departure_date = self.invoice_requisites['invoice_date']
        invoice_object.title = self.file_name
        invoice_object.invoice_number = int(self.invoice_requisites['invoice_number'])
        recipient_obj = Recipient.get_object('id', self.invoice_requisites['recipient_id'])
        invoice_object.recipient = recipient_obj
        invoice_object.save()

class GiisReportParser:
    def __init__(self, file_handler_obj):
        Request.printCreateObject(self)
        self.file_handler_obj = file_handler_obj
        self.products_queryset = Jewelry.get_all_obj()
        self.uins_list = [product.uin for product in self.products_queryset]
        self.manufacturers_list = Manufacturer.get_all_values_list('inn')
        self.products_dicts_dict = giis_file_parsing(self)
