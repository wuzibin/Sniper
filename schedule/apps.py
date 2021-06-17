from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedule'
    verbose_name = '计划任务管理'
