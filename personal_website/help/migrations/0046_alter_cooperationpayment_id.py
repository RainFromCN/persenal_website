# Generated by Django 4.1 on 2023-08-19 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0045_cooperationpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooperationpayment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
