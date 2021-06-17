from django.contrib import admin
from .models import APIInfo
from django.db.models import JSONField
from jsoneditor.forms import JSONEditor


@admin.register(APIInfo)
class DBInfoDisplay(admin.ModelAdmin):
    list_display = (
        'api_id', 'api_nickname', 'api_type',
        'api_addr', 'api_username', 'api_password',
        'api_last_modify')  # 展示的列表
    list_display_links = ('api_nickname',)  # 可点击链接
    search_fields = ('api_nickname', 'api_addr')  # 搜索字段
    list_filter = ('api_type',)  # 过滤字段
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }
