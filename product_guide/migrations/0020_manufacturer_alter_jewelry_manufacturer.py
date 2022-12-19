# Generated by Django 4.0.6 on 2022-11-05 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0019_remove_jewelry_trademark'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Производитель')),
                ('inn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ИНН')),
            ],
            options={
                'verbose_name': 'Производителя',
                'verbose_name_plural': 'Производители',
            },
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.manufacturer', verbose_name='Производитель'),
        ),
    ]
