from product_guide.models import File, OutgoingInvoice, Counterparties
from django.core.exceptions import ObjectDoesNotExist
from product_guide.services.anover_functions import form_type_check, get_outgoing_invoice_title_list, \
    get_context_for_product_list
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.invoice_parser import invoice_parsing, word_invoice_parsing
from product_guide.services.readers import read_excel_file, read_msword_file


def set_correct_file_name(file_name):

    if ' ' in file_name:
        file_name = file_name.replace(' ', '_')
    if '№' in file_name:
        file_name = file_name.replace('№', '')

    return file_name


def determine_belonging_file(file_name):

    if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
        return 'msexcel'
    elif file_name.endswith('.doc') or file_name.endswith('.docx'):
        return 'msword'


def save_form(form):
    file_object = None
    try:
        file_object = File.get_object('title', form.title)
    except ObjectDoesNotExist:
        pass
    if file_object:
        file_object.delete()

    form.save()
    file_object = File.objects.latest('id')
    file_object.title = form.title
    file_object.save()


def file_processing(file_name, file_path):
    invoice_requisites = {}
    file_type = determine_belonging_file(file_name)
    if file_type == 'msexcel':
        full_rows_list, sheet, file_type = read_excel_file(file_path)
        if form_type_check(file_name) == 'giis_report':
            products_dicts_dict = giis_file_parsing(full_rows_list, sheet)
            invoice_session_data = {'giis_report': True}
            invoice_requisites['invoice_type'] = 'giis_report'

        else:
            products_dicts_dict, invoice_requisites = invoice_parsing(full_rows_list, sheet, file_type,
                                                                      file_name)

            invoice_session_data = {
                'giis_report': False,
                'arrival_date': invoice_requisites['arrival_date'],
                'invoice_number': invoice_requisites['invoice_number'],
                'provider_id': invoice_requisites['provider_id'],
                'recipient': invoice_requisites['recipient_id'],
                'title': file_name
            }
        context = get_context_for_product_list(products_dicts_dict, page_num=None)
        template_path = 'product_guide\product_base_v2.html'
        print(invoice_requisites)
        if invoice_requisites['invoice_type'] == 'incoming':
            context['invoice_title'] = file_name
            context['invoice_date'] = invoice_requisites['arrival_date']
            context['invoice_number'] = invoice_requisites['invoice_number']
            context['provider'] = Counterparties.get_object('id', invoice_requisites['provider_id'])
            template_path = 'product_guide\show_incoming_invoice.html'
        print(context)

        return context, products_dicts_dict, invoice_session_data, template_path

    elif file_type == 'msword':
        # print('WORD')

        header_table, product_table = read_msword_file(file_path)
        products_dicts_dict, invoice_requisites = word_invoice_parsing(header_table, product_table)

        if invoice_requisites['provider_id'] == 1:
            if file_name in get_outgoing_invoice_title_list(OutgoingInvoice.get_all_obj()):
                invoice_object = OutgoingInvoice.get_object('title', file_name)
                invoice_object.delete()

            invoice_object = OutgoingInvoice()
            invoice_object.departure_date = invoice_requisites['departure_date']
            invoice_object.title = file_name
            invoice_object.invoice_number = int(invoice_requisites['invoice_number'])
            invoice_object.recipient_id = invoice_requisites['recipient_id']
            invoice_object.save()

        context = get_context_for_product_list(products_dicts_dict, page_num=None)
        context['recipient'] = Counterparties.get_object('id', invoice_requisites['recipient_id'])
        context['departure_date'] = invoice_requisites['departure_date']
        context['invoice_title'] = file_name.split('.')[0]
        context['file_path'] = file_path
        context['file_name'] = file_name
        invoice_session_data = invoice_requisites
        template_path = 'product_guide\show_outgoing_invoice.html'
        print(context)
        return context, products_dicts_dict, invoice_session_data, template_path
