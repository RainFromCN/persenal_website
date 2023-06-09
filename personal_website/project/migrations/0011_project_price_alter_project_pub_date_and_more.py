# Generated by Django 4.1 on 2023-06-01 09:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_purchase_date_alter_project_pub_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='price',
            field=models.IntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 53, 9, 633006, tzinfo=datetime.timezone.utc), verbose_name='data published'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 53, 9, 634008, tzinfo=datetime.timezone.utc), verbose_name='purchase date'),
        ),
    ]
