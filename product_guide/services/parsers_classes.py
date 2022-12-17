from product_guide.models import Jewelry, Manufacturer
from product_guide.services.giis_parser import giis_file_parsing
from product_guide.services.request_classes import Request


class ExcelParser:
    pass


class WordParser:
    pass


class GiisReportParser:
    pass
    # def __init__(self, file_handler_obj):
    #     Request.printCreateObject(self)
    #     self.file_handler_obj = file_handler_obj
    #     self.products_queryset = Jewelry.get_all_obj()
    #     self.uins_list = [product.uin for product in self.products_queryset]
    #     self.manufacturers_list = Manufacturer.get_all_values_list('inn')
    #     self.products_dicts_dict = giis_file_parsing(self)

class KonturReportParser:
    pass


class IncomingInvoiceParser:
    pass


class OutgoingInvoiceParser:
    pass



