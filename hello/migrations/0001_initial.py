# Generated by Django 4.1.7 on 2023-08-08 15:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='db_model',
            fields=[
                ('id_number', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('alumni', models.BooleanField(default=False)),
                ('release_info', models.BooleanField(default=False)),
                ('checked_in', models.BooleanField(default=False)),
                ('checked_in_time', models.DateTimeField(auto_now=True)),
                ('table_number', models.IntegerField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Master_list',
            },
        ),
        migrations.CreateModel(
            name='import_csv',
            fields=[
                ('id_number', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('alumni', models.BooleanField(default=False)),
                ('release_info', models.BooleanField(default=False)),
                ('table_number', models.IntegerField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='LogMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=300)),
                ('log_date', models.DateTimeField(verbose_name='date logged')),
            ],
        ),
        migrations.CreateModel(
            name='Pass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=100)),
                ('pass_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hello.db_model')),
            ],
        ),
    ]