# Generated by Django 4.1.7 on 2023-09-11 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0002_alter_import_csv_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='db_model',
            name='first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='db_model',
            name='last_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
