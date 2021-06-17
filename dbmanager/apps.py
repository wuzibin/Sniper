from django.apps import AppConfig


class DbmanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dbmanager'
    verbose_name = '数据库管理'
