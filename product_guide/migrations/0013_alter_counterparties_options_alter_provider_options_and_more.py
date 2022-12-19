# Generated by Django 4.0.6 on 2022-10-11 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0012_counterparties_alter_provider_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='counterparties',
            options={'verbose_name': 'Контрагент', 'verbose_name_plural': 'Контрагенты'},
        ),
        migrations.AlterModelOptions(
            name='provider',
            options={'verbose_name': 'Поставщик', 'verbose_name_plural': 'Поставщики'},
        ),
        migrations.RenameField(
            model_name='jewelry',
            old_name='input_invoice',
            new_name='input_invoice_id',
        ),
        migrations.RenameField(
            model_name='jewelry',
            old_name='outgoing_invoice',
            new_name='outgoing_invoice_id',
        ),
        migrations.RenameField(
            model_name='jewelry',
            old_name='provider',
            new_name='provider_id',
        ),
        migrations.RenameField(
            model_name='jewelry',
            old_name='recipient',
            new_name='recipient_id',
        ),
    ]
