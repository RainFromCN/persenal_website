# Generated by Django 4.1 on 2023-06-01 09:27

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_alter_project_pub_date_remove_user_project_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='author_id',
        ),
        migrations.RemoveField(
            model_name='user',
            name='project',
        ),
        migrations.AlterField(
            model_name='project',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 6, 1, 9, 27, 54, 679543, tzinfo=datetime.timezone.utc), verbose_name='data published'),
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prj_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='project.project')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='project.user')),
            ],
        ),
    ]
