# Generated by Django 4.1 on 2023-08-01 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0021_alter_project_prj_id_alter_user_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='field',
            field=models.CharField(choices=[(0, '自动化/控制工程'), (1, '计算机'), (2, '机械'), (3, '土木'), (4, '电气'), (5, '生物'), (6, '环境'), (7, '化学'), (8, '材料')], default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='school',
            field=models.CharField(default=0, max_length=20),
            preserve_default=False,
        ),
    ]