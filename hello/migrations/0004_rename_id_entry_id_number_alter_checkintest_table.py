# Generated by Django 4.1.7 on 2023-06-15 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0003_checkintest_rename_log_entry'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='id',
            new_name='id_number',
        ),
        migrations.AlterModelTable(
            name='checkintest',
            table='Checkin_test',
        ),
    ]
