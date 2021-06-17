from django.db import models
from django.db.models import JSONField


class APIInfo(models.Model):
    api_id = models.AutoField(verbose_name='#', primary_key=True)
    api_type = models.IntegerField(verbose_name='接口类型', choices=[(1, 'HTTP/HTTPS'), (2, 'WebSocket')], default=1)
    api_nickname = models.CharField(verbose_name='接口名称', max_length=128)
    api_addr = models.CharField(verbose_name='接口地址', max_length=256)
    # api_method = models.IntegerField(verbose_name='请求方式', choices=[(1, 'POST'), (2, 'GET')], default=1)
    api_username = models.CharField(verbose_name='接口登录用户名', max_length=64, blank=True)  # 有的接口可能不需要登录
    api_password = models.CharField(verbose_name='接口登录密码', max_length=64, blank=True)
    # api_params = JSONField(verbose_name='请求参数', blank=True)  # 请求参数可能为空
    api_last_modify = models.DateTimeField(verbose_name='上一次修改时间', auto_now=True)

    class Meta:
        db_table = "API_INFO"
        verbose_name = '接口信息'
        verbose_name_plural = verbose_name
        ordering = ['api_id']

    def __str__(self):
        return self.api_nickname
