# Generated by Django 4.0.6 on 2022-10-11 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0013_alter_counterparties_options_alter_provider_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counterparties',
            name='full_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Полное наименование поставщика'),
        ),
        migrations.AlterField(
            model_name='inputinvoice',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Поставщик'),
        ),
        migrations.AlterField(
            model_name='outgoinginvoice',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Поставщик'),
        ),
    ]
