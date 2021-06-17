from django.db import models
from django.db.models import ForeignKey
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from dbmanager.models import DBConnInfo
from apimanager.models import APIInfo
from django.db.models import JSONField
from django.contrib import messages

# task_type_choices = [(1, '执行SQL'), (2, '接口检查')]
api_method_choices = [('POST', 'POST'), ('GET', 'GET')]


class ScheduleExtInfo(models.Model):
    s_id = models.AutoField(verbose_name='#', primary_key=True)
    schedule_task = ForeignKey(PeriodicTask, verbose_name='计划任务', on_delete=models.CASCADE)
    # task_type = models.IntegerField(verbose_name='任务类型', choices=task_type_choices, default=1)
    # 运行SQL参数
    run_db = ForeignKey(DBConnInfo, verbose_name='SQL运行数据库', on_delete=models.PROTECT, blank=True, null=True)
    exec_sql = models.TextField(verbose_name='SQL语句', blank=True, null=True)
    sql_alert = models.CharField(verbose_name='SQL告警条件', blank=True, null=True, max_length=1024)
    # 接口请求所需参数
    check_api = ForeignKey(APIInfo, verbose_name='检测接口', blank=True, null=True, on_delete=models.PROTECT)
    api_method = models.TextField(verbose_name='请求方式', choices=api_method_choices, blank=True, null=True, max_length=10)
    api_header = JSONField(verbose_name='请求头', blank=True, null=True)
    api_params = JSONField(verbose_name='请求参数', blank=True, null=True)
    api_alert = models.CharField(verbose_name='API告警条件', blank=True, null=True, max_length=1024)

    # 告警方式（SMTP、接口）、重试次数 TODO
    def delete(self):
        if self.schedule_task.crontab:
            crontab_id = self.schedule_task.crontab.id
            query_cron = PeriodicTask.objects.filter(crontab_id=crontab_id)
            if len(query_cron) == 1:  # 只有自己用
                print('仅当前任务使用Crontab:', query_cron[0], '，删除')
                self.schedule_task.crontab.delete()
        self.schedule_task.delete()
        super(ScheduleExtInfo, self).delete()

    class Meta:
        db_table = "SCHEDULE_EXT_INFO"
        verbose_name = '计划任务信息'
        verbose_name_plural = verbose_name
        ordering = ['s_id']

    def __str__(self):
        return self.schedule_task.name
