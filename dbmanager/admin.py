from django.contrib import admin
from dbmanager.models import *


class DBInfoDisplay(admin.ModelAdmin):
    list_display = (
        'db_id', 'db_nickname', 'db_type',
        'db_host', 'db_port',
        'db_username', 'db_password', 'db_name', 'db_last_modify')  # 展示的列表
    list_display_links = ('db_nickname',)  # 可点击链接
    search_fields = ('db_nickname', 'db_host')  # 搜索字段
    list_filter = ('db_type',)  # 过滤字段


admin.site.register(DBConnInfo, DBInfoDisplay)

'''
class DBCronTabDisplay(admin.ModelAdmin):
    fields = ['job_name', 'db_info', 'job_cron', 'job_params']  # 显示表单
    list_display = [
        'job_id', 'job_name', 'db_info',
        'job_cron', 'job_status',
        'job_modifier', 'job_modify_time', 'job_creator', 'job_create_time']  # 展示的列表
    list_display_links = ['job_name']  # 可点击链接
    search_fields = ['job_name', 'db_info']  # 搜索字段
    list_filter = ['job_status', 'job_creator', 'job_modifier']  # 过滤字段
'''

# admin.site.register(DBCrontab, DBCronTabDisplay)

admin.site.site_header = 'OSS'  # 设置header
admin.site.site_title = '定时任务管理系统'  # 设置title
