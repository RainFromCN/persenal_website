# Generated by Django 4.1 on 2023-06-14 09:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_alter_project_introduction_alter_project_paper_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='price',
            field=models.FloatField(default=9.9),
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 14, 9, 47, 48, 649326, tzinfo=datetime.timezone.utc), verbose_name='data published'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 14, 9, 47, 48, 650328, tzinfo=datetime.timezone.utc), verbose_name='purchase date'),
        ),
    ]