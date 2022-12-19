# Generated by Django 4.0.6 on 2022-10-11 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0014_alter_counterparties_full_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inputinvoice',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='outgoinginvoice',
            name='provider',
        ),
        migrations.AlterField(
            model_name='outgoinginvoice',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Получатель'),
        ),
    ]
