# schedule_tasks/schedules/tasks.py
from __future__ import absolute_import, unicode_literals
import time
from celery import shared_task

from .models import ScheduleExtInfo
from .utils import db_exec_sql


@shared_task(name='测试任务')
def exec_sql(task_id):
    query_task = ScheduleExtInfo.objects.filter(schedule_task__id=task_id)
    if len(query_task) != 1:
        raise ValueError('计划任务有误，请联系管理员')
    task = query_task[0]
    print(task)
    return f'Hello Celery, the task id is: {task_id}'


@shared_task(name='接口检测')
def api_check(task_id):
    query_task = ScheduleExtInfo.objects.filter(schedule_task__id=task_id)
    if len(query_task) != 1:
        raise ValueError('计划任务有误，请联系管理员')
    task = query_task[0]
    print(task)
    return f'Hello Celery, the task id is: {task_id}'


@shared_task(name='执行SQL')
def exec_sql(task_id):
    query_task = ScheduleExtInfo.objects.filter(schedule_task__id=task_id)
    if len(query_task) != 1:
        raise ValueError('计划任务有误，请联系管理员')
    task = query_task[0]
    return db_exec_sql(task)
