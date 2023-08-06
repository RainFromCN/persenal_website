# Generated by Django 4.1 on 2023-08-04 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0026_user_positive_times_user_pub_times'),
        ('help', '0008_rename_req_id_request_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Procedure',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.user')),
            ],
        ),
        migrations.RemoveField(
            model_name='requestfollows',
            name='notify_new_bids',
        ),
        migrations.CreateModel(
            name='ProcedureStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('discription', models.CharField(max_length=100)),
                ('pay', models.IntegerField()),
                ('procedure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help.procedure')),
            ],
        ),
    ]