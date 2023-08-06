# Generated by Django 4.1 on 2023-08-05 05:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0010_requestfollows_procedure'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cooperation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('follow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help.requestfollows')),
            ],
        ),
        migrations.AddField(
            model_name='procedurestep',
            name='state',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='CooperationMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('img_id', models.CharField(max_length=200)),
                ('cooperation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='help.cooperation')),
            ],
        ),
    ]
