# Generated by Django 4.0.6 on 2022-12-19 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_guide', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counterparties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=70, null=True, verbose_name='Полное наименование поставщика')),
                ('first_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Имя')),
                ('surname', models.CharField(blank=True, max_length=30, null=True, verbose_name='Фамилия')),
                ('last_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Отчество')),
                ('short_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='ФИО')),
                ('inn', models.IntegerField(blank=True, null=True, verbose_name='ИНН')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('tel', models.IntegerField(blank=True, null=True, verbose_name='Телефон')),
                ('checking_account', models.IntegerField(blank=True, null=True, verbose_name='Рассчетный счет')),
                ('bank', models.CharField(blank=True, max_length=50, null=True, verbose_name='Банк')),
                ('bik', models.IntegerField(blank=True, null=True, verbose_name='БИК')),
                ('address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Контрагента',
                'verbose_name_plural': 'Контрагенты',
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Имя файла')),
                ('file', models.FileField(upload_to='product_guide/documents/', verbose_name='Файл')),
            ],
            options={
                'verbose_name': 'Файл',
                'verbose_name_plural': 'Файлы',
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Производитель')),
                ('inn', models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='ИНН')),
            ],
            options={
                'verbose_name': 'Производителя',
                'verbose_name_plural': 'Производители',
            },
        ),
        migrations.CreateModel(
            name='Metal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, verbose_name='Металл')),
            ],
            options={
                'verbose_name': 'Металл',
                'verbose_name_plural': 'Металлы',
            },
        ),
        migrations.AlterModelOptions(
            name='jewelry',
            options={'ordering': ['metal', 'name', 'weight'], 'verbose_name': 'Изделие', 'verbose_name_plural': 'Изделия'},
        ),
        migrations.RemoveField(
            model_name='jewelry',
            name='giis_reg_status',
        ),
        migrations.AddField(
            model_name='jewelry',
            name='arrival_date',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Дата прихода'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='departure_date',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Дата отгрузки'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='purchase_price',
            field=models.FloatField(blank=True, null=True, verbose_name='Закупочная цена'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='selling_price',
            field=models.FloatField(blank=True, null=True, verbose_name='Отпускная цена'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='size',
            field=models.FloatField(blank=True, null=True, verbose_name='Размер'),
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='coating',
            field=models.CharField(blank=True, choices=[('Чернение', 'Чернение'), ('Золочение', 'Золочение'), ('Родирование', 'Родирование'), ('Оксидирование', 'Оксидирование')], max_length=20, null=True, verbose_name='Покрытие'),
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='giis_status',
            field=models.CharField(blank=True, choices=[('На хранении', 'На хранении'), ('Выведено', 'Выведено')], max_length=20, null=True, verbose_name='Статус ГИИС'),
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='metal',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Металл'),
        ),
        migrations.AlterField(
            model_name='jewelry',
            name='vendor_code',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Артикул'),
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Получатель')),
                ('counterparties', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Контрагент')),
            ],
            options={
                'verbose_name': 'Грузополучателя',
                'verbose_name_plural': 'Грузополучатели',
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='Поставщик')),
                ('counterparties', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.counterparties', verbose_name='Контрагент')),
            ],
            options={
                'verbose_name': 'Поставщика',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='OutgoingInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=30, null=True, verbose_name='Накладная')),
                ('invoice_number', models.IntegerField(blank=True, null=True, verbose_name='Номер накладной')),
                ('departure_date', models.CharField(blank=True, max_length=20, null=True, verbose_name='Дата отгрузки')),
                ('recipient', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.recipient', verbose_name='Получатель')),
            ],
            options={
                'verbose_name': 'Исходящую накладную',
                'verbose_name_plural': 'Исходящие накладные',
            },
        ),
        migrations.CreateModel(
            name='InputInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=30, null=True, verbose_name='Накладная')),
                ('invoice_number', models.IntegerField(blank=True, null=True, verbose_name='Номер накладной')),
                ('arrival_date', models.CharField(blank=True, max_length=20, null=True, verbose_name='Дата прихода')),
                ('provider', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.provider', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'Входящую накладную',
                'verbose_name_plural': 'Входящие накладные',
            },
        ),
        migrations.AddField(
            model_name='jewelry',
            name='input_invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.inputinvoice', verbose_name='Входящая накладная'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.manufacturer', verbose_name='Производитель'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='outgoing_invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.outgoinginvoice', verbose_name='Исходящая накладная'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.provider', verbose_name='Поставщик'),
        ),
        migrations.AddField(
            model_name='jewelry',
            name='recipient',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='product_guide.recipient', verbose_name='Получатель'),
        ),
    ]
