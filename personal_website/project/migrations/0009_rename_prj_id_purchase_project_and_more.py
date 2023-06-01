# Generated by Django 4.1 on 2023-06-01 09:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_remove_project_author_id_remove_user_project_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='prj_id',
            new_name='project',
        ),
        migrations.RenameField(
            model_name='purchase',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 40, 38, 496985, tzinfo=datetime.timezone.utc), verbose_name='data published'),
        ),
    ]