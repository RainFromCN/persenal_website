# Generated by Django 4.1 on 2023-08-20 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0046_alter_cooperationpayment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cooperation',
            name='client_deposit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='server_deposit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='cooperationpayment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]