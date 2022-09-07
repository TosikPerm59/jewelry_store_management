from django.db import models
from django.contrib.auth.models import User



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
    giis_reg_statuses = (
        ('Зарегистрирован', 'Зарегистрирован'),
        ('Не зарегистрирован', 'Не зарегистрирован')
    )

    giis_statuses = (
        ('Числится на хранении', 'Числится на хранении'),
        ('Выбыл из ГИИС', 'Выбыл из ГИИС')
    )

    name = models.CharField(max_length=20, verbose_name='Вид изделия')
    metal = models.ForeignKey('Metal', on_delete=models.PROTECT, verbose_name='Металл')
    weight = models.FloatField(verbose_name='Вес')
    vendor_code = models.CharField(max_length=15, verbose_name='Артикул', blank=True, null=True)
    barcode = models.IntegerField(verbose_name='Штрихкод', blank=True, null=True, unique=True)
    uin = models.IntegerField(verbose_name='УИН', blank=True, null=True, unique=True)
    coating = models.CharField(max_length=20, verbose_name='Покрытие', blank=True, null=True, choices=coatings)
    inserts = models.CharField(max_length=50, verbose_name='Вставки', blank=True, null=True)
    availability_status = models.CharField(max_length=50, verbose_name='Статус наличия')
    giis_reg_status = models.CharField(max_length=50, verbose_name='Статус регистрации в ГИИС', choices=giis_reg_statuses)
    giis_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='Статус ГИИС', choices=giis_statuses)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Цена')
    price_per_gram = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Цена за грамм')
    provider = models.ForeignKey('Provider', null=True, blank=True, verbose_name='Поставщик', on_delete=models.PROTECT)
    arrival_date = models.DateField(null=True, blank=True, verbose_name='Дата прихода')
    input_invoice = models.ForeignKey('InputInvoice', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Входящая накладная')
    outgoing_invoice = models.ForeignKey('OutgoingInvoice', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Исходящая накладная')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель', blank=True, null=True)
    trademark = models.CharField(max_length=30, verbose_name='Торговая марка', blank=True, null=True)

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


class Invoice(models.Model):
    provider = models.ForeignKey('Provider', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Поставщик')
    invoice_number = models.IntegerField(null=True, blank=True, verbose_name='Номер накладной')
    recipient = models.ForeignKey('Recipient', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Получатель')

    class Meta:
        abstract = True


class InputInvoice(Invoice, models.Model):
    arrival_date = models.DateField(null=True, blank=True, verbose_name='Дата прихода')

    class Meta:
        verbose_name = 'Входящая накладная'
        verbose_name_plural = 'Входящие накладные'


class OutgoingInvoice(Invoice, models.Model):
    departure_date = models.DateField(null=True, blank=True, verbose_name='Дата отгрузки')

    class Meta:
        verbose_name = 'Исходящая накладная'
        verbose_name_plural = 'Исходящие накладные'


class Provider(models.Model):
    full_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Полное наименование поставщика')
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
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Recipient(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Имя')
    surname = models.CharField(max_length=30, blank=True, null=True, verbose_name='Фамилия')
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')
    short_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='ФИО')
    inn = models.IntegerField(verbose_name='ИНН', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    tel = models.IntegerField(blank=True, null=True, verbose_name='Телефон')
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Грузополучатель'
        verbose_name_plural = 'Грузополучатели'