# Generated by Django 3.2.3 on 2021-05-21 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apimanager', '0004_alter_apiinfo_api_params'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiinfo',
            name='api_params',
            field=models.JSONField(blank=True, verbose_name='请求参数'),
        ),
    ]
