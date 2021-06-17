import traceback
from datetime import datetime

from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule, ClockedSchedule, SolarSchedule
from schedule.models import ScheduleExtInfo
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from .utils import task_param_check
import json
import pytz
from celery import current_app
from django.contrib import messages

system_task = ['celery.starmap', 'celery.accumulate', 'celery.chord', 'celery.backend_cleanup', 'celery.chunks',
               'celery.chord_unlock', 'celery.group', 'celery.map', 'celery.chain']


def support_task(request):
    try:
        current_app.loader.import_default_modules()
        all_tasks = current_app.tasks.keys()
        ret_list = list(set(all_tasks) - set(system_task))
        return JsonResponse({"code": 0, "support_task": ret_list, "msg": '查询任务类型成功'})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


def add_schedule(request):
    try:
        if request.method == 'POST':
            req = request.POST.dict()
            print(req)
            # 参数校验 TODO
            task_param_check(req)
            if req.get('start_time', None):
                start_time = datetime.strptime(req['start_time'], '%Y-%m-%d %H:%M:%S')
            else:
                start_time = None
            if req.get('exec_sql', None):
                exec_sql = req['exec_sql'][:-1] if req['exec_sql'].endswith(';') else req['exec_sql']
            else:
                exec_sql = ''
            task_obj = PeriodicTask.objects.create(name=req['task_name'], task=req['task_type'],
                                                   description=req['description']
                                                   if req.get('description', None) else '',
                                                   enabled=1 if req['enabled'] == 'true' else 0,
                                                   one_off=1 if req['one_off'] == 'true' else 0,
                                                   start_time=start_time,
                                                   crontab_id=req['crontab']
                                                   if req['schedule_type'] == 'crontab' else None,
                                                   interval_id=req['interval']
                                                   if req['schedule_type'] == 'interval' else None,
                                                   clocked_id=req['clocked']
                                                   if req['schedule_type'] == 'clocked' else None,
                                                   )
            task_obj.args = '[' + str(task_obj.id) + ']'
            task_obj.save()
            schedule_obj = ScheduleExtInfo.objects.create(schedule_task_id=task_obj.id, run_db_id=req['run_db'],
                                                          exec_sql=exec_sql,
                                                          sql_alert=req['sql_alert'],
                                                          check_api_id=req['check_api'], api_method=req['api_method'],
                                                          api_header=req['api_header'], api_params=req['api_params'],
                                                          api_alert=req['api_alert'])
            msg = '成功新增了计划任务 “<a href="/admin/schedule/scheduleextinfo/{}/change/">{}</a>”。'
            messages.add_message(request, messages.SUCCESS, msg.format(schedule_obj.s_id, task_obj.name))
            return JsonResponse(
                {"code": 0, "task": str(schedule_obj.s_id) + ':' + str(schedule_obj), "msg": "create task success."})
        else:
            raise TypeError('请求方式错误，仅支持POST')
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"code": 1, "msg": repr(e)})


def schedule_by_id(request, task_id):
    print('task_id:', task_id)
    try:
        query_task = ScheduleExtInfo.objects.filter(s_id=task_id)
        if len(query_task) != 1:
            raise ValueError('No such task: ' + str(len(query_task)))

        if request.method == 'GET':
            task = query_task[0]
            task_ret = model_to_dict(task.schedule_task)
            if task_ret['start_time'] is None:
                task_ret['start_time'] = ''
            ret = model_to_dict(task)
            ret['task'] = task_ret
            return JsonResponse({"code": 0, "task_info": ret, "msg": "query crontab success."})

        if request.method == 'POST':
            req = request.POST.dict()
            print(req)
            # 参数校验 TODO
            task_param_check(req)
            if req.get('start_time', None):
                start_time = datetime.strptime(req['start_time'], '%Y-%m-%d %H:%M:%S')
            else:
                start_time = None
            if req.get('exec_sql', None):
                exec_sql = req['exec_sql'][:-1] if req['exec_sql'].endswith(';') else req['exec_sql']
            else:
                exec_sql = ''

            schedule_obj = query_task[0]
            task_obj = schedule_obj.schedule_task
            task_obj.name = req['task_name']
            task_obj.task = req['task_type']
            task_obj.description = req['description'] if req.get('description', None) else ''
            task_obj.enabled = 1 if req['enabled'] == 'true' else 0
            task_obj.one_off = 1 if req['one_off'] == 'true' else 0
            task_obj.start_time = start_time
            if req['schedule_type'] == 'crontab':
                task_obj.crontab_id = req['crontab']
                task_obj.interval = None
                task_obj.clocked = None
            elif req['schedule_type'] == 'interval':
                task_obj.interval_id = req['interval']
                task_obj.crontab = None
                task_obj.clocked = None
            elif req['schedule_type'] == 'clocked':
                task_obj.clocked_id = req['clocked']
                task_obj.crontab = None
                task_obj.interval = None
            task_obj.save()

            schedule_obj.run_db_id = req['run_db']
            schedule_obj.exec_sql = exec_sql
            schedule_obj.sql_alert = req['sql_alert']
            schedule_obj.check_api_id = req['check_api']
            schedule_obj.api_method = req['api_method']
            schedule_obj.api_header = req['api_header']
            schedule_obj.api_params = req['api_params']
            schedule_obj.api_alert = req['api_alert']
            schedule_obj.save()
            msg = '成功修改了计划任务 “<a href="/admin/schedule/scheduleextinfo/{}/change/">{}</a>”。'
            messages.add_message(request, messages.SUCCESS, msg.format(schedule_obj.s_id, task_obj.name))
            return JsonResponse({"code": 0, "msg": "提交成功"})
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"code": 1, "msg": repr(e)})


def crontab_timezone(request):
    try:
        with open('schedule/resource/timezones.json', 'r') as json_data:
            tz_list = json.load(json_data)
            return JsonResponse({"code": 0, "timezones": tz_list, "msg": "query timezone success."}, safe=False)
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


cron_param = ['day_of_month', 'day_of_week', 'hour', 'minute', 'month_of_year', 'timezone']


# @login_required
def crontab_schedule(request):
    try:
        if request.method == "GET":
            query_cron = CrontabSchedule.objects.all()
            json_cron = serializers.serialize('json', query_cron)
            return JsonResponse({"code": 0, "crontab": eval(json_cron), "msg": "query crontab success."}, safe=False)

        if request.method == "POST":
            req = request.POST.dict()
            for key in cron_param:
                if req.get(key, None) is None:
                    raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            req['timezone'] = pytz.timezone(req['timezone'])
            new_cron = CrontabSchedule(**req)
            new_cron.save()
            ret = model_to_dict(new_cron)
            ret['timezone'] = str(ret['timezone'])
            return JsonResponse({"code": 0, "crontab": ret, "msg": "提交成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


def crontab_by_id(request, crontab_id):
    print('crontab_id:', crontab_id)
    try:
        query_cron = CrontabSchedule.objects.filter(id=crontab_id)
        if len(query_cron) != 1:
            raise ValueError('No such crontab: ' + str(len(query_cron)))

        if request.method == 'GET':
            cron = query_cron[0]
            ret = model_to_dict(cron)
            ret['timezone'] = str(ret['timezone'])
            return JsonResponse({"code": 0, "crontab": ret, "msg": "query crontab success."})

        if request.method == 'POST':
            req = request.POST.dict()
            for key in cron_param:
                if req.get(key, None) is None:
                    raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            req['timezone'] = pytz.timezone(req['timezone'])
            query_cron.update(**req)
            ret = model_to_dict(query_cron[0])
            ret['timezone'] = str(ret['timezone'])
            return JsonResponse({"code": 0, "crontab": ret, "msg": "提交Crontab成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


interval_param = ['every', 'period']


def interval_schedule(request):
    try:
        if request.method == "GET":
            query_interval = IntervalSchedule.objects.all()
            json_interval = serializers.serialize('json', query_interval)
            return JsonResponse({"code": 0, "interval": eval(json_interval), "msg": "query interval success."},
                                safe=False)

        if request.method == "POST":
            req = request.POST.dict()
            for key in interval_param:
                if req.get(key, None) is None:
                    raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            new_interval = IntervalSchedule(**req)
            new_interval.save()
            ret = model_to_dict(new_interval)
            return JsonResponse({"code": 0, "interval": ret, "msg": "提交成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


def interval_by_id(request, interval_id):
    print('interval_id:', interval_id)
    try:
        query_interval = IntervalSchedule.objects.filter(id=interval_id)
        if len(query_interval) != 1:
            raise ValueError('No such interval: ' + str(len(query_interval)))

        if request.method == 'GET':
            interval = query_interval[0]
            ret = model_to_dict(interval)
            return JsonResponse({"code": 0, "interval": ret, "msg": "query interval success."})

        if request.method == 'POST':
            req = request.POST.dict()
            for key in interval_param:
                if req.get(key, None) is None:
                    raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            query_interval.update(**req)
            ret = model_to_dict(query_interval[0])
            return JsonResponse({"code": 0, "interval": ret, "msg": "提交Interval成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


def clocked_schedule(request):
    try:
        if request.method == "GET":
            query_clocked = ClockedSchedule.objects.all()
            json_clocked = serializers.serialize('json', query_clocked)
            return JsonResponse({"code": 0, "clocked": eval(json_clocked), "msg": "query clocked success."},
                                safe=False)

        if request.method == "POST":
            req = request.POST.dict()
            print(req)
            if req.get('clocked_time', None) is None:
                raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            clocked_time = datetime.strptime(req['clocked_time'], "%Y-%m-%d %H:%M:%S")
            new_interval = ClockedSchedule(clocked_time=clocked_time)
            new_interval.save()
            ret = model_to_dict(new_interval)
            return JsonResponse({"code": 0, "clocked": ret, "msg": "提交成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})


def clocked_by_id(request, clocked_id):
    print('clocked_id:', clocked_id)
    try:
        query_clocked = ClockedSchedule.objects.filter(id=clocked_id)
        if len(query_clocked) != 1:
            raise ValueError('No such clocked: ' + str(len(query_clocked)))

        if request.method == 'GET':
            clocked = query_clocked[0]
            ret = model_to_dict(clocked)
            return JsonResponse({"code": 0, "clocked": ret, "msg": "query clocked success."})

        if request.method == 'POST':
            req = request.POST.dict()
            print(req)
            if req.get('clocked_time', None) is None:
                raise ValueError('传入参数有误')
            for val in req.values():
                if not val or not val.strip():
                    raise ValueError('传入参数存在空值')
            clocked_time = datetime.strptime(req['clocked_time'], "%Y-%m-%d %H:%M:%S")
            query_clocked.update(clocked_time=clocked_time)
            ret = model_to_dict(query_clocked[0])
            return JsonResponse({"code": 0, "clocked": ret, "msg": "提交Clocked成功"})
    except Exception as e:
        return JsonResponse({"code": 1, "msg": repr(e)})
