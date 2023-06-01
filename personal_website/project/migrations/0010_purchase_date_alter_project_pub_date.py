# Generated by Django 4.1 on 2023-06-01 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_rename_prj_id_purchase_project_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 44, 22, 296502, tzinfo=datetime.timezone.utc), verbose_name='purchase date'),
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 44, 22, 295502, tzinfo=datetime.timezone.utc), verbose_name='data published'),
        ),
    ]
