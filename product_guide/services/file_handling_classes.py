import os
from product_guide.models import OutgoingInvoice, Jewelry, Manufacturer, Recipient, Provider, IncomingInvoice, Invoice
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.invoice_parser import word_invoice_parsing, invoice_parsing
from product_guide.services.parsers_classes import GiisReportParser, Torg12ExcelParser
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

        print('Выполняется функция extract_data_from_file')

        if self.file_extension == 'xls' or self.file_extension == 'xlsx':
            self.file_app = 'MS Excel'
            return ReadExcelFile(self)
        elif self.file_extension == 'doc' or self.file_extension == 'docx':
            self.file_app = 'MS Word'
            return ReadWordFile(self)

    def parsing_data_object(self):
        print('Выполняется функция parsing_data_object')
        if self.file_app == 'MS Excel':
            print('MS Excel')
            print(''.join(self.file_data_obj.rows_list[0]))

            if self.request_obj.file_name.startswith('4_BATCH_LIST_PRINT'):
                self.invoice_requisites['invoice_type'] = 'giis_report'
                self.request_obj.template_path = 'product_guide/show_giis_report.html'
                return GiisReportParser(self).products_dicts_dict

            elif ''.join(self.file_data_obj.rows_list[0]).find('торг-12'):
                torg12_excel_parser = Torg12ExcelParser(self)
                self.invoice_requisites = torg12_excel_parser.invoice_requisites
                self.request_obj.template_path = 'product_guide/show_incoming_invoice.html'
                return torg12_excel_parser.products_dicts_dict

            # products_dicts_dict, self.invoice_requisites = invoice_parsing(self.file_data_obj.rows_list, self.file_data_obj.sheet, self.file_extension)
            # self.provider_obj = Provider.get_object('id', self.invoice_requisites['provider_id'])
            # self.recipient_obj = Recipient.get_object('id', self.invoice_requisites['recipient_id'])
            # print('self.invoice_requisites[recipient_id] = ', self.invoice_requisites['recipient_id'])
            # print('self.recipient_obj = ', self.recipient_obj)
            # if self.recipient_obj.counterparties.surname == 'Александрова':
            #     print('INCOMING')
            #     self.invoice_requisites['invoice_type'] = 'incoming_invoice'
            #     self.request_obj.template_path = 'product_guide/show_outgoing_invoice.html'
            #     self.save_invoice()
            #     return products_dicts_dict

        elif self.file_app == 'MS Word':
            print('MS Word')
            products_dicts_dict, self.invoice_requisites = word_invoice_parsing(self.file_data_obj.header_table, self.file_data_obj.product_table)
            self.provider_obj = Provider.get_object('id', self.invoice_requisites['provider_id'])
            self.recipient_obj = Recipient.get_object('id', self.invoice_requisites['recipient_id'])

            if self.provider_obj.counterparties.surname == 'Александрова':
                self.invoice_requisites['invoice_type'] = 'outgoing_invoice'
                print('OUTGOING')
                self.request_obj.template_path = 'product_guide/show_outgoing_invoice.html'
                self.save_invoice()
                return products_dicts_dict
            #
            # if self.recipient_obj.counterparties.surname == 'Александрова':
            #     print('INCOMING')
            #     self.invoice_requisites['invoice_type'] = 'incoming_invoice'
            #     self.request_obj.template_path = 'product_guide/show_outgoing_invoice.html'



    def save_invoice(self):
        print('Выполняется функция save_invoice')
        invoice_object = Invoice

        if self.file_name in OutgoingInvoice.get_all_values_list('title') + IncomingInvoice.get_all_values_list('title'):
            return

        if self.invoice_requisites['invoice_type'] == 'incoming_invoice':
            invoice_object = IncomingInvoice()
            invoice_object.arrival_date = self.invoice_requisites['invoice_date']
            invoice_object.provider = self.provider_obj

        elif self.invoice_requisites['invoice_type'] == 'outgoing_invoice':
            invoice_object = OutgoingInvoice()
            invoice_object.departure_date = self.invoice_requisites['invoice_date']
            invoice_object.recipient = self.recipient_obj

        invoice_object.title = self.file_name
        invoice_object.invoice_number = int(self.invoice_requisites['invoice_number'])
        invoice_object.save()

    # def save_outgoing_invoice_object(self, recipient_obj):
    #     if self.file_name in OutgoingInvoice.get_all_values_list('title'):
    #         return
    #
    #     invoice_object = OutgoingInvoice()
    #     invoice_object.departure_date = self.invoice_requisites['invoice_date']
    #     invoice_object.title = self.file_name
    #     invoice_object.invoice_number = int(self.invoice_requisites['invoice_number'])
    #     invoice_object.recipient = recipient_obj
    #     invoice_object.save()
    #
    # def save_incoming_invoice_object(self, provider_obj):
    #     if self.file_name in IncomingInvoice.get_all_values_list('title'):
    #         return
    #
    #     invoice_object = IncomingInvoice()
    #     invoice_object.arrival_date = self.invoice_requisites['invoice_date']
    #     invoice_object.title = self.file_name
    #     invoice_object.invoice_number = int(self.invoice_requisites['invoice_number'])
    #     invoice_object.provider = provider_obj
    #     invoice_object.save()

# class GiisReportParser:
#     def __init__(self, file_handler_obj):
#         Request.printCreateObject(self)
#         self.file_handler_obj = file_handler_obj
#         self.products_queryset = Jewelry.get_all_obj()
#         self.uins_list = [product.uin for product in self.products_queryset]
#         self.manufacturers_list = Manufacturer.get_all_values_list('inn')
#         self.products_dicts_dict = giis_file_parsing(self)
