from product_guide.models import File, OutgoingInvoice, Counterparties
from django.core.exceptions import ObjectDoesNotExist
from product_guide.services.anover_functions import determine_giis_report, get_outgoing_invoice_title_list, \
    get_context_for_product_list, find_products_in_db
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.invoice_parser import invoice_parsing, word_invoice_parsing
from product_guide.services.readers import read_excel_file, read_msword_file


def determine_belonging_file(file_name):
    """Определение типа файла.
    Функция принимает имя файла, возвращает строку 'msexcel' или 'msword'."""

    if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
        return 'msexcel'
    elif file_name.endswith('.doc') or file_name.endswith('.docx'):
        return 'msword'


def file_processing(self):
    """Функция обработки входящих файлов. Определяет тип, и производит парсинг файла.
    Принимает имя и путь к файлу, возвращает: контекст, dict изделий, данные
    о накладной для сессии, путь к шаблону"""
    invoice_requisites = {}
    # Определение типа файла.
    file_type = determine_belonging_file(self.file_name)
    # Если тип файла Excel
    if file_type == 'msexcel':
        print('Чтение файла')
        full_rows_list, sheet, file_type = read_excel_file(self.temp_file['file'])  # Чтение файла Excel
        # Если файл является отчетом ГИИС
        if determine_giis_report(self.file_name) == 'giis_report':
            # Парсинг файла отчета ГИИС
            products_dicts_dict = giis_file_parsing(full_rows_list, sheet)
            invoice_data = {'giis_report': True}
            invoice_requisites['invoice_type'] = 'giis_report'

        else:
            #  Парсинг накладной
            products_dicts_dict, invoice_requisites = invoice_parsing(full_rows_list, sheet, file_type,
                                                                      self.file_name)
            #  Данные для сохранения в сесии
            invoice_data = {
                'giis_report': False,
                'arrival_date': invoice_requisites['arrival_date'],
                'invoice_number': invoice_requisites['invoice_number'],
                'provider_id': invoice_requisites['provider_id'],
                'recipient_id': invoice_requisites['recipient_id'],
                'title': self.file_name,
            }
        #  Создание контекста для рэндэринга
        context = get_context_for_product_list(products_dicts_dict, page_num=None)

        template_path = 'product_guide\product_base_v2.html'
        # Если накладная является входящей, то в контекст добавляются дополнительные данные
        if invoice_requisites['invoice_type'] == 'incoming':
            context['prod_list'] = find_products_in_db(products_dicts_dict)
            context['invoice_title'] = self.file_name
            context['file_path'] = self.file_path
            context['invoice_date'] = invoice_requisites['arrival_date']
            context['invoice_number'] = invoice_requisites['invoice_number']
            context['provider_surname'] = Counterparties.get_object('id', invoice_requisites['provider_id']).surname
            template_path = 'product_guide\show_incoming_invoice.html'


        # print(products_dicts_dict)
        # print(context)
        return context, products_dicts_dict, invoice_data, template_path

    elif file_type == 'msword':
        # print('WORD')

        header_table, product_table = read_msword_file(self.temp_file['file'])
        products_dicts_dict, invoice_requisites = word_invoice_parsing(header_table, product_table)

        if invoice_requisites['provider_id'] == 1:
            if self.file_name in get_outgoing_invoice_title_list(OutgoingInvoice.get_all_obj()):
                invoice_object = OutgoingInvoice.get_object('title', self.file_name)
                invoice_object.delete()

            invoice_object = OutgoingInvoice()
            invoice_object.departure_date = invoice_requisites['departure_date']
            invoice_object.title = self.file_name
            invoice_object.invoice_number = int(invoice_requisites['invoice_number'])
            invoice_object.recipient_id = invoice_requisites['recipient_id']
            invoice_object.save()

        context = get_context_for_product_list(products_dicts_dict, page_num=None)
        context['recipient'] = Counterparties.get_object('id', invoice_requisites['recipient_id'])
        context['departure_date'] = invoice_requisites['departure_date']
        context['invoice_title'] = self.file_name.split('.')[0]
        # context['file_path'] = file_path
        context['file_name'] = self.file_name
        invoice_data = invoice_requisites
        template_path = 'product_guide\show_outgoing_invoice.html'

        # print(products_dicts_dict)
        # print(context)
        return context, products_dicts_dict, invoice_data, template_path
