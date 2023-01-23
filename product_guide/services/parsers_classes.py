from product_guide.models import Jewelry, Manufacturer, Counterparties, Provider, Recipient
from product_guide.services.finders import find_name, find_metal, find_size, find_barcode, find_art, find_uin_in_string
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.request_classes import Request
from product_guide.services.validity import isfloat, isinteger


class ExcelParser:
    pass


class WordParser:
    pass


class GiisReportParser:
    def __init__(self, file_handler_obj):
        Request.printCreateObject(self)
        self.file_handler_obj = file_handler_obj
        self.products_queryset = Jewelry.get_all_obj()
        self.uins_list = [product.uin for product in self.products_queryset]
        self.manufacturers_list = Manufacturer.get_all_values_list('inn')
        self.products_dicts_dict = giis_file_parsing(self)


class KonturReportParser:
    pass


class OutgoingInvoiceParser:
    pass


class IncomingInvoiceParser:
    pass


class Torg12ExcelParser:

    def __init__(self, file_handler_obj):
        Request.printCreateObject(self)
        self.file_handler_obj = file_handler_obj
        self.requisites_block, self.table_header_block, self.table_body_block = self.blocks_definition()
        self.invoice_requisites = RequisitesParser(self.requisites_block).requisites_dict
        self.products_dicts_dict = TableParser(self).products_dicts_dict

    def blocks_definition(self):
        print('Выполняется функция blocks_definition')
        start, finish = None, None
        rows_list = self.file_handler_obj.file_data_obj.rows_list
        for counter, row in enumerate(rows_list):
            start = counter if 'страница 1' in row else start
            finish = counter if 'всего по накладной ' in row else finish
            if start and finish:
                return rows_list[:start], rows_list[start + 1: start + 3], rows_list[start + 4: finish]

    @staticmethod
    def get_filtered_string(insert_string):
        filterable_items = ['"', '(', ')', ';']
        for item in filterable_items:
            insert_string = insert_string.replace(item, '', insert_string.count(item))

        return insert_string


class RequisitesParser:
    def __init__(self, requisites_block):
        Request.printCreateObject(self)
        self.requisites_block = requisites_block
        self.requisites_dict = self.get_requisition_dict()

    def get_requisition_dict(self):
        print('Выполняется функция get_requisition_dict')
        requisites_dict = {'provider_string': None, 'recipient_string': None}
        for row in self.requisites_block:
            if 'поставщик' in row and requisites_dict['provider_string'] is None:
                requisites_dict['provider_string'] = self.create_clear_string(row)
            if 'грузополучатель' in row or 'плательщик' in row and requisites_dict['recipient_string'] is None:
                requisites_dict['recipient_string'] = self.create_clear_string(row)
            if 'товарная накладная  ' in row or 'товарная накладная ' in row:
                requisites_dict['invoice_number'] = self.get_invoice_number(row)
                requisites_dict['invoice_date'] = self.get_invoice_date(row)

        requisites_dict = self.definition_invoice_type_provider_recipient(requisites_dict)

        return requisites_dict

    @staticmethod
    def create_clear_string(row):
        print('Выполняется функция create_clear_string')
        clear_string = ''

        for elem in row:
            if isinstance(elem, str) and elem != '' and elem is not None:
                clear_string += elem + ' '

        clear_string = Torg12ExcelParser.get_filtered_string(clear_string)
        return clear_string

    @staticmethod
    def get_invoice_date(row):
        print('Выполняется функция get_invoice_date')
        invoice_date = row[15]
        if invoice_date is None or invoice_date == '':
            invoice_date = row[21]
            if invoice_date is None or invoice_date == '':
                invoice_date = row[13]
        return invoice_date

    @staticmethod
    def get_invoice_number(row):
        print('Выполняется функция get_invoice_number')
        invoice_number = row[12]
        if invoice_number is None or invoice_number == '':
            invoice_number = row[18]
            if invoice_number is None or invoice_number == '':
                invoice_number = row[8]
        return invoice_number

    @staticmethod
    def definition_invoice_type_provider_recipient(requisitions_dict):
        print('Выполняется функция definition_invoice_type_provider_recipient')
        counterparties_queryset, provider_obj, recipient_obj = Counterparties.get_all_obj(),  None, None
        for counterparties_obj in counterparties_queryset:
            if provider_obj is None and requisitions_dict['provider_string'].find(counterparties_obj.surname.lower()) != -1:
                provider_obj = RequisitesParser.get_or_create_provider_obj(counterparties_obj)
                requisitions_dict['provider_id'] = provider_obj.id
                requisitions_dict['invoice_type'] = 'outgoing' if counterparties_obj.surname == 'Александрова'\
                    else 'incoming'

            if recipient_obj is None and requisitions_dict['recipient_string'].find(counterparties_obj.surname.lower()) != -1:
                recipient_obj = RequisitesParser.get_or_create_recipient_obj(counterparties_obj)
                requisitions_dict['recipient_id'] = recipient_obj.id
                requisitions_dict['invoice_type'] = 'incoming' if counterparties_obj.surname == 'Александрова'\
                    else 'outgoing'
            if provider_obj and recipient_obj:
                break
        return requisitions_dict

    @staticmethod
    def get_or_create_provider_obj(counterparties_obj):
        print('Выполняется функцтя get_or_create_provider_obj')
        if isinstance(counterparties_obj, Counterparties):
            provider_obj = Provider.get_object('counterparties_id', counterparties_obj.id)
            if provider_obj is None:
                provider_obj = Provider(
                    title=counterparties_obj.short_name,
                    counterparties=counterparties_obj
                )
                provider_obj.save()
            return provider_obj

    @staticmethod
    def get_or_create_recipient_obj(counterparties_obj):
        print('Выполняется функция get_or_create_recipient_obj')
        if isinstance(counterparties_obj, Counterparties):
            recipient_obj = Recipient.get_object('counterparties_id', counterparties_obj.id)
            if recipient_obj:
                return recipient_obj

            recipient_obj = Recipient(
                title=counterparties_obj.short_name,
                counterparties=counterparties_obj
            )
            recipient_obj.save()
            return recipient_obj


class TableParser:
    def __init__(self, torg12_excel_parser):
        self.torg12_excel_parser = torg12_excel_parser
        self.column_indexes_dict = self.column_indexes_definition()
        self.product_list = self.get_product_list()
        self.products_dicts_dict = self.get_products_dicts_dict()

    def column_indexes_definition(self):
        print('Выполняется функция column_indexes_definition')
        column_indexes_dict = {}
        for row in self.torg12_excel_parser.table_header_block:
            for elem in row:
                if isinstance(elem, str) and elem != '':
                    if elem.find('наименование') != -1:
                        column_indexes_dict['product_ind'] = row.index(elem)
                    if elem.find('нетто') != -1:
                        column_indexes_dict['weight_ind'] = row.index(elem)
                    if elem.find('сумма с учетом') != -1 or elem.find('сумма сучетом') != -1:
                        column_indexes_dict['price_ind'] = row.index(elem)
                    if elem.find('цена') != -1:
                        column_indexes_dict['price_per_gram_ind'] = row.index(elem)
                    if elem.find('уин') != -1:
                        column_indexes_dict['uin_ind'] = row.index(elem)
        return column_indexes_dict

    def get_product_list(self):
        print('Выполняется функция get_product_list')
        index_number, product_list = 1, []
        for row in self.torg12_excel_parser.table_body_block:

            descr = ''
            row_start_index, row_finish_index = None, None

            if isinteger(row[1]) and int(row[1]) == index_number or isfloat(row[1]) and int(row[1]) == index_number:
                index_number += 1
                row_start_index = self.torg12_excel_parser.table_body_block.index(row)

                for row_2 in self.torg12_excel_parser.table_body_block[row_start_index + 1:]:
                    if (isinteger(row_2[1]) and int(row_2[1]) == int(row[1]) + 1 or isfloat(row_2[1])
                            and int(row_2[1]) == int(row[1]) + 1 or 'итого ' in row_2):
                        row_finish_index = self.torg12_excel_parser.table_body_block.index(row_2)
                        break

                for row_3 in self.torg12_excel_parser.table_body_block[row_start_index: row_finish_index]:
                    if self.torg12_excel_parser.file_handler_obj.file_extension == 'xls':
                        descr += (row_3[2] + ' ' + row_3[12] + ' ').lower()
                    else:
                        descr += (row_3[2] + ' ' + row_3[6] + ' ').lower() if row_3[6] is not None else ''
                        descr += (row_3[2] + ' ' + row_3[12] + ' ').lower() if row_3[12] is not None else ''

                descr = descr.replace('\n', ' ') if '\n' in descr else descr
                descr = descr.replace('шк:', ' ') if 'шк:' in descr else descr
                descr = descr.replace('бирка:', ' ') if 'бирка:' in descr else descr
                descr = descr.replace('  ', ' ') if '  ' in descr else descr
                row[2] = descr
                product_list.append(row)
        # print(*product_list)
        return product_list

    def get_products_dicts_dict(self):
        product_dicts_dict = {}
        for counter, product in enumerate(self.product_list, 1):
            description_string = product[self.column_indexes_dict['product_ind']].lower()
            description_string = Torg12ExcelParser.get_filtered_string(description_string)
            split_description_string = description_string.split(' ')

            prod_name = find_name(description_string)
            prod_metal = find_metal(description_string)
            prod_size = find_size(split_description_string, group='excel')
            prod_weight = product[self.column_indexes_dict['weight_ind']]
            prod_art = find_art(description_string, group='excel')
            prod_barcode = find_barcode(description_string)
            prod_price = product[self.column_indexes_dict['price_ind']]
            prod_uin = product[self.column_indexes_dict['uin_ind']] if 'uin_ind' in self.column_indexes_dict.keys() else None

            if prod_uin is None:
                prod_uin = find_uin_in_string(description_string)
            if prod_metal is None:
                price_per_gram = prod_price / prod_weight
                if price_per_gram > 2500:
                    prod_metal = 'Золото 585'
                else:
                    prod_metal = 'Серебро 925'

            product_dict = {'name': prod_name,
                            'metal': prod_metal,
                            'barcode': prod_barcode,
                            'uin': prod_uin,
                            'weight': round(float(prod_weight), ndigits=2),
                            'vendor_code': prod_art,
                            'size': round(float(prod_size), ndigits=2) if isfloat(prod_size) else None,
                            'price': round(float(prod_price), ndigits=2),
                            'number': counter
                            }
            product_dicts_dict[counter] = product_dict

        return product_dicts_dict
