# Generated by Django 4.1 on 2023-08-18 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0027_remove_user_positive_times'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(auto_now=True),
        ),
    ]