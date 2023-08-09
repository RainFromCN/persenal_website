# Generated by Django 4.1 on 2023-08-09 10:47

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0026_user_positive_times_user_pub_times'),
        ('help', '0021_cooperation_acceptance_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CooperationChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
            ],
        ),
        migrations.AlterField(
            model_name='cooperation',
            name='request_document_update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 9, 10, 47, 29, 858223, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='CooperationMessage',
        ),
        migrations.AddField(
            model_name='cooperationchatmessage',
            name='cooperation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help.cooperation'),
        ),
        migrations.AddField(
            model_name='cooperationchatmessage',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.user'),
        ),
    ]
