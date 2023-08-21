# Generated by Django 4.1 on 2023-08-16 01:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0025_remove_cooperation_acceptance_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cooperation',
            name='client_deposit',
            field=models.IntegerField(blank=True, default=None),
        ),
        migrations.AddField(
            model_name='cooperation',
            name='server_deposit',
            field=models.IntegerField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='request_document_update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 16, 1, 14, 18, 105009, tzinfo=datetime.timezone.utc)),
        ),
    ]