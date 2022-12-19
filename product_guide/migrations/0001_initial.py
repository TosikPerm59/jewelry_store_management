from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Jewelry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Вид изделия')),
                ('metal', models.CharField(choices=[('gold', 'Золото 585'), ('silver', 'Серебро 925')], max_length=11, verbose_name='Металл')),
                ('weight', models.FloatField(verbose_name='Вес')),
                ('vendor_code', models.CharField(max_length=15, verbose_name='Артикул')),
                ('barcode', models.IntegerField(blank=True, null=True, unique=True, verbose_name='Штрихкод')),
                ('uin', models.IntegerField(blank=True, null=True, unique=True, verbose_name='УИН')),
                ('coating', models.CharField(blank=True, choices=[('black', 'Чернение'), ('gold', 'Золочение'), ('rhodium', 'Родирование'), ('oxide', 'Оксидирование')], max_length=20, null=True, verbose_name='Покрытие')),
                ('inserts', models.CharField(blank=True, max_length=50, null=True, verbose_name='Вставки')),
                ('availability_status', models.CharField(max_length=50, verbose_name='Статус наличия')),
                ('giis_reg_status', models.CharField(choices=[('yes', 'Зарегистрирован в ГИИС'), ('no', 'Не зарегистрирован в ГИИС')], max_length=50, verbose_name='Статус наличия')),
                ('giis_status', models.CharField(choices=[('listed', 'Числится на хранении'), ('dropped_out', 'Выбыл из ГИИС')], max_length=20, null=True, unique=True, verbose_name='Статус ГИИС')),
            ],
        ),
    ]