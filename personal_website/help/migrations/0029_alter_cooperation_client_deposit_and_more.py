# Generated by Django 4.1 on 2023-08-16 01:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0028_alter_cooperation_client_deposit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooperation',
            name='client_deposit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='request_document_update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 16, 1, 19, 50, 924438, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='server_deposit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
    ]
