# Generated by Django 4.0.6 on 2022-11-11 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0020_manufacturer_alter_jewelry_manufacturer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jewelry',
            options={'ordering': ['metal', 'name', 'weight'], 'verbose_name': 'Изделие', 'verbose_name_plural': 'Изделия'},
        ),
        migrations.AddField(
            model_name='provider',
            name='counterparties',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Контрагент'),
        ),
        migrations.AlterField(
            model_name='inputinvoice',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.provider', verbose_name='Поставщик'),
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='vendor_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Артикул'),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='inn',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='outgoinginvoice',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.recipient', verbose_name='Получатель'),
        ),
    ]
