from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class ExtendedModelsModel(models.Model):

    def __str__(self):
        if hasattr(self, 'name'):
            if self.name is not None:
                return self.name
            else:
                return '-'
        if hasattr(self, 'title'):
            if self.title is not None:
                return self.title
            else:
                return '-'
        if hasattr(self, 'surname'):
            if self.surname is not None:
                return self.surname
            else:
                return '-'

    @classmethod
    def get_all_obj(cls):
        return cls.objects.all()

    @classmethod
    def get_all_values(cls):
        return cls.objects.all().values()

    @classmethod
    def get_object(cls, attr, value):
        obj = None
        try:
            if hasattr(cls, attr):
                if attr == 'name':
                    obj = cls.objects.get(name=value)
                if attr == 'title':
                    obj = cls.objects.get(title=value)
                if attr == 'uin':
                    obj = cls.objects.get(uin=value)
                if attr == 'id':
                    obj = cls.objects.get(id=value)
                if attr == 'barcode':
                    obj = cls.objects.get(barcode=value)
                if attr == 'vendor_code':
                    obj = cls.objects.get(vendor_code=value)
                if attr == 'inn':
                    obj = cls.objects.get(inn=value)
            return obj
        except ObjectDoesNotExist:
            pass

    @classmethod
    def get_all_values_list(cls, attr_name):
        values_list = []
        for product_dict in cls.get_all_values():
            if attr_name in product_dict.keys():
                if product_dict[attr_name] is not None:
                    values_list.append(product_dict[attr_name])
        return values_list

    @classmethod
    def delete_all_objects(cls):
        objects = cls.objects.all()
        if objects:
            for obj in objects:
                obj.delete()

    class Meta:
        abstract = True


    @classmethod
    def find_product(cls, product):
        """ Функция поиска позиций в таблицах базы данных. На вход подается словарь"""
        try:
            if product['uin'] != 'None' or product['uin'] is not None:
                return cls.get_object('uin', int(product['uin']))

            elif product['barcode'] != 'None' or product['barcode'] is not None:
                return cls.get_object('barcode', int(product['barcode']))
        except:
            pass

class Jewelry(ExtendedModelsModel):
    metals = (
        ('Золото 585', 'Золото 585'),
        ('Серебро 925', 'Серебро 925')
    )
    coatings = (
        ('Чернение', 'Чернение'),
        ('Золочение', 'Золочение'),
        ('Родирование', 'Родирование'),
        ('Оксидирование', 'Оксидирование')
    )

    giis_statuses = (
        ('На хранении', 'На хранении'),
        ('Выведено', 'Выведено')
    )

    availability_statuses = (
        ('В наличии', 'В наличии'),
        ('Продано', 'Продано'),
        ('Передано', 'Передано'),
        ('Передано по договору', 'Передано по договору')
    )

    name = models.CharField(max_length=20, verbose_name='Вид изделия')
    metal = models.CharField(max_length=15, verbose_name='Металл', blank=True, null=True)
    weight = models.FloatField(verbose_name='Вес')
    size = models.FloatField(verbose_name='Размер', blank=True, null=True)
    vendor_code = models.CharField(max_length=20, verbose_name='Артикул', blank=True, null=True)
    barcode = models.IntegerField(verbose_name='Штрихкод', blank=True, null=True, unique=True)
    uin = models.IntegerField(verbose_name='УИН', blank=True, null=True, unique=True)
    coating = models.CharField(max_length=20, verbose_name='Покрытие', blank=True, null=True, choices=coatings)
    inserts = models.CharField(max_length=50, verbose_name='Вставки', blank=True, null=True)
    purchase_price = models.FloatField(null=True, blank=True, verbose_name='Закупочная цена')
    arrival_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата прихода')
    provider = models.ForeignKey('Provider', null=True, blank=True, verbose_name='Поставщик', on_delete=models.PROTECT)
    input_invoice = models.ForeignKey('InputInvoice', null=True, blank=True, on_delete=models.PROTECT,
                                      verbose_name='Входящая накладная')
    availability_status = models.CharField(max_length=50, choices=availability_statuses, verbose_name='Статус наличия')
    giis_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='Статус ГИИС',
                                   choices=giis_statuses)
    departure_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата отгрузки')
    selling_price = models.FloatField(null=True, blank=True, verbose_name='Отпускная цена')
    recipient = models.ForeignKey('Recipient', null=True, blank=True, on_delete=models.PROTECT, default=None,
                                  verbose_name='Получатель')
    outgoing_invoice = models.ForeignKey('OutgoingInvoice', null=True, blank=True, on_delete=models.PROTECT,
                                         verbose_name='Исходящая накладная')
    manufacturer = models.ForeignKey('Manufacturer', null=True, blank=True, verbose_name='Производитель',
                                     on_delete=models.PROTECT)


    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'
        ordering = ['metal', 'name', 'weight']


class Metal(ExtendedModelsModel):
    name = models.CharField(max_length=15, verbose_name='Металл')

    class Meta:
        verbose_name = 'Металл'
        verbose_name_plural = 'Металлы'


class File(ExtendedModelsModel):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Имя файла')
    file = models.FileField(upload_to='product_guide/documents/', verbose_name='Файл')

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class Invoice(ExtendedModelsModel):
    title = models.CharField(max_length=30, null=True, blank=True, verbose_name='Накладная')
    invoice_number = models.IntegerField(null=True, blank=True, verbose_name='Номер накладной')

    class Meta:
        abstract = True


class InputInvoice(Invoice, ExtendedModelsModel):
    provider = models.ForeignKey('Provider', null=True, blank=True, on_delete=models.PROTECT, default=None,
                                 verbose_name='Поставщик')
    arrival_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата прихода')

    class Meta:
        verbose_name = 'Входящую накладную'
        verbose_name_plural = 'Входящие накладные'


class OutgoingInvoice(Invoice, ExtendedModelsModel):
    recipient = models.ForeignKey('Recipient', null=True, blank=True, on_delete=models.PROTECT, default=None,
                                  verbose_name='Получатель')
    departure_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата отгрузки')

    class Meta:
        verbose_name = 'Исходящую накладную'
        verbose_name_plural = 'Исходящие накладные'


class Counterparties(ExtendedModelsModel):
    full_name = models.CharField(max_length=70, blank=True, null=True, verbose_name='Полное наименование поставщика')
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Имя')
    surname = models.CharField(max_length=30, blank=True, null=True, verbose_name='Фамилия')
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')
    short_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='ФИО')
    inn = models.IntegerField(verbose_name='ИНН', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    tel = models.IntegerField(blank=True, null=True, verbose_name='Телефон')
    checking_account = models.IntegerField(blank=True, null=True, verbose_name='Рассчетный счет')
    bank = models.CharField(max_length=50, blank=True, null=True, verbose_name='Банк')
    bik = models.IntegerField(blank=True, null=True, verbose_name='БИК')
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Контрагента'
        verbose_name_plural = 'Контрагенты'


class Provider(ExtendedModelsModel):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Поставщик')
    counterparties = models.ForeignKey('Counterparties', null=True, blank=True, on_delete=models.PROTECT, default=None,
                                       verbose_name='Контрагент')

    class Meta:
        verbose_name = 'Поставщика'
        verbose_name_plural = 'Поставщики'


class Recipient(ExtendedModelsModel):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Получатель')
    counterparties = models.ForeignKey('Counterparties', null=True, blank=True, on_delete=models.PROTECT, default=None,
                                       verbose_name='Контрагент')

    class Meta:
        verbose_name = 'Грузополучателя'
        verbose_name_plural = 'Грузополучатели'


class Manufacturer(ExtendedModelsModel):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Производитель')
    inn = models.CharField(max_length=50, blank=True, null=True, verbose_name='ИНН', unique=True)

    class Meta:
        verbose_name = 'Производителя'
        verbose_name_plural = 'Производители'
