from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class Jewelry(models.Model):

    def __str__(self):
        return self.name

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
        ('Выбыл', 'Выбыл')
    )

    availability_statuses = (
        ('В наличии', 'В наличии'),
        ('Продано', 'Продано'),
        ('Передано', 'Передано')
    )

    name = models.CharField(max_length=20, verbose_name='Вид изделия')
    metal = models.CharField(max_length=15, verbose_name='Металл', blank=True, null=True)
    weight = models.FloatField(verbose_name='Вес')
    size = models.FloatField(verbose_name='Размер', blank=True, null=True)
    vendor_code = models.CharField(max_length=15, verbose_name='Артикул', blank=True, null=True)
    barcode = models.IntegerField(verbose_name='Штрихкод', blank=True, null=True, unique=True)
    uin = models.IntegerField(verbose_name='УИН', blank=True, null=True, unique=True)
    coating = models.CharField(max_length=20, verbose_name='Покрытие', blank=True, null=True, choices=coatings)
    inserts = models.CharField(max_length=50, verbose_name='Вставки', blank=True, null=True)
    availability_status = models.CharField(max_length=50, verbose_name='Статус наличия')
    giis_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='Статус ГИИС', choices=giis_statuses)
    price = models.FloatField(null=True, blank=True, verbose_name='Цена')
    provider_id = models.ForeignKey('Provider', null=True, blank=True, verbose_name='Поставщик', on_delete=models.PROTECT)
    arrival_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата прихода')
    input_invoice_id = models.ForeignKey('InputInvoice', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Входящая накладная')
    outgoing_invoice_id = models.ForeignKey('OutgoingInvoice', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Исходящая накладная')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель', blank=True, null=True)
    trademark = models.CharField(max_length=30, verbose_name='Торговая марка', blank=True, null=True)
    recipient_id = models.ForeignKey('Recipient', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Получатель')

    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'
        ordering = ['metal', 'name', '-weight']


class Metal(models.Model):
    name = models.CharField(max_length=15, verbose_name='Металл')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Металл'
        verbose_name_plural = 'Металлы'


class File(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Имя файла')
    file = models.FileField(upload_to='product_guide/documents/', verbose_name='Файл')

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'


class Invoice(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=30, null=True, blank=True, verbose_name='Накладная')
    invoice_number = models.IntegerField(null=True, blank=True, verbose_name='Номер накладной')

    class Meta:
        abstract = True


class InputInvoice(Invoice, models.Model):
    provider = models.ForeignKey('Counterparties', null=True, blank=True, on_delete=models.PROTECT,
                                 verbose_name='Поставщик')
    arrival_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата прихода')

    class Meta:
        verbose_name = 'Входящую накладную'
        verbose_name_plural = 'Входящие накладные'


class OutgoingInvoice(Invoice, models.Model):
    recipient = models.ForeignKey('Counterparties', null=True, blank=True, on_delete=models.PROTECT,
                                  verbose_name='Получатель')
    departure_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='Дата отгрузки')

    class Meta:
        verbose_name = 'Исходящую накладную'
        verbose_name_plural = 'Исходящие накладные'


class Counterparties(models.Model):

    def __str__(self):
        return self.short_name

    full_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='Полное наименование поставщика')
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Имя')
    surname = models.CharField(max_length=30, blank=True, null=True, verbose_name='Фамилия')
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')
    short_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='ФИО')
    inn = models.IntegerField(verbose_name='ИНН', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    tel = models.IntegerField(blank=True, null=True, verbose_name='Телефон')
    checking_account = models.IntegerField(blank=True, null=True, verbose_name='Рассчетный сет')
    bank = models.CharField(max_length=50, blank=True, null=True, verbose_name='Банк')
    bik = models.IntegerField(blank=True, null=True, verbose_name='БИК')
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Контрагента'
        verbose_name_plural = 'Контрагенты'


class Provider(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Поставщик')

    class Meta:
        verbose_name = 'Поставщика'
        verbose_name_plural = 'Поставщики'


class Recipient(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='Получатель')

    class Meta:
        verbose_name = 'Грузополучателя'
        verbose_name_plural = 'Грузополучатели'

