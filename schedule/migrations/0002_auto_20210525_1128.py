# Generated by Django 3.2.3 on 2021-05-25 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scheduleextinfo',
            options={'ordering': ['s_id'], 'verbose_name': '计划任务信息', 'verbose_name_plural': '计划任务信息'},
        ),
        migrations.AlterModelTable(
            name='scheduleextinfo',
            table='SCHEDULE_EXT_INFO',
        ),
    ]
