# Generated by Django 4.1 on 2023-08-15 05:52

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0024_alter_cooperation_request_document_update_datetime_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cooperation',
            name='acceptance_date',
        ),
        migrations.RemoveField(
            model_name='cooperation',
            name='acceptance_date_fix',
        ),
        migrations.RemoveField(
            model_name='cooperation',
            name='acceptance_date_fix_state',
        ),
        migrations.RemoveField(
            model_name='cooperation',
            name='predict_finish_date',
        ),
        migrations.RemoveField(
            model_name='cooperation',
            name='predict_finish_date_fix',
        ),
        migrations.RemoveField(
            model_name='cooperation',
            name='predict_finish_date_fix_state',
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='request_document_update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 15, 5, 52, 29, 37797, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='ProcedureSubstep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.BooleanField()),
                ('content', models.CharField(max_length=100)),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help.procedurestep')),
            ],
        ),
    ]
