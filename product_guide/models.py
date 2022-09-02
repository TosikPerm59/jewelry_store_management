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
    metal = models.CharField(max_length=11, verbose_name='Металл', choices=metals)
    weight = models.FloatField(verbose_name='Вес')
    vendor_code = models.CharField(max_length=15, verbose_name='Артикул', blank=True, null=True)
    barcode = models.IntegerField(verbose_name='Штрихкод', blank=True, null=True, unique=True)
    uin = models.IntegerField(verbose_name='УИН', blank=True, null=True, unique=True)
    coating = models.CharField(max_length=20, verbose_name='Покрытие', blank=True, null=True, choices=coatings)
    inserts = models.CharField(max_length=50, verbose_name='Вставки', blank=True, null=True)
    availability_status = models.CharField(max_length=50, verbose_name='Статус наличия')
    giis_reg_status = models.CharField(max_length=50, verbose_name='Статус регистрации в ГИИС', choices=giis_reg_statuses)
    giis_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='Статус ГИИС', choices=giis_statuses)

    class Meta:
        verbose_name = 'Изделие'
        verbose_name_plural = 'Изделия'
        ordering = ['metal', 'name', '-weight']



class Rings(Jewelry):
    pass
#
# class Wicker(Jewelry):
#     weaving = models.CharField(max_length=20, verbose_name='Плетение', blank=True, null=True)
#
# class Necklace(Jewelry):
#     pass

