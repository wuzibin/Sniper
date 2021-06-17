from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model

db_type_choices = [(1, 'Oracle'), (2, 'Mysql'), (3, 'Redis')]


class DBConnInfo(models.Model):
    db_id = models.AutoField(verbose_name='#', primary_key=True)
    db_type = models.IntegerField(verbose_name='数据库类型', choices=db_type_choices, default=1)
    db_nickname = models.CharField(verbose_name='数据库别名', max_length=128)
    db_host = models.CharField(verbose_name='数据库主机', max_length=128)
    db_port = models.IntegerField(verbose_name='端口号',
                                  validators=[MaxValueValidator(65535), MinValueValidator(0)])
    db_username = models.CharField(verbose_name='数据库用户名', max_length=64, blank=True)  # redis 不需要用户名
    db_password = models.CharField(verbose_name='数据库密码', max_length=64)
    db_name = models.CharField(verbose_name='数据库名称', max_length=64, blank=True)
    db_last_modify = models.DateTimeField(verbose_name='上一次修改时间', auto_now=True)

    # def get_conn_str(self):

    class Meta:
        db_table = "DB_CONN_INFO"
        verbose_name = '数据库连接信息'
        verbose_name_plural = verbose_name
        ordering = ['db_id']

    def __str__(self):
        return self.db_nickname


'''
class DBCrontab(models.Model):
    job_id = models.AutoField(verbose_name='#', primary_key=True)
    job_name = models.CharField(verbose_name='计划任务名称', max_length=128)
    db_info = models.ForeignKey(DBConnInfo, verbose_name='数据库', on_delete=models.PROTECT)
    job_cron = models.CharField(verbose_name='时间表达式', max_length=128)
    job_params = MonacoEditorModelField(verbose_name='任务参数')
    job_status = models.IntegerField(verbose_name='任务状态', choices=[(0, '停止'), (1, '运行中')], default=0)
    job_creator = models.ForeignKey(get_user_model(), verbose_name='创建者', related_name='job_creator',
                                    on_delete=models.PROTECT)
    job_create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    job_modifier = models.ForeignKey(get_user_model(), verbose_name='修改者', related_name='job_modifier',
                                     on_delete=models.PROTECT)
    job_modify_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = '数据库计划任务'
        verbose_name_plural = verbose_name
        ordering = ['job_id']

    def __str__(self):
        return self.job_name
'''

# class CrontabCliJob(CrontabBaseJob):
