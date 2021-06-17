import json
import traceback
from datetime import datetime

from dbmanager.models import db_type_choices
import sys
import time
import cx_Oracle
import sqlparse
import pymysql
import redis

alert_str = """
if {}:
    alert_fun()
else:
    print('Nothing to do')
"""


# 工具类 实现命令执行 邮件发送等
def db_exec_sql(task):
    run_db = task.run_db
    db_dict = dict(db_type_choices)
    if run_db.db_type not in db_dict:
        raise ValueError('数据库类型不在支持列表中，请联系管理员')
    db_type_name = db_dict.get(run_db.db_type)
    exec_fun = getattr(sys.modules[__name__], str.lower(db_type_name) + '_exec')
    return exec_fun(task)


def oracle_exec(task):
    run_db = task.run_db
    dsn = cx_Oracle.makedsn(run_db.db_host, run_db.db_port, service_name=run_db.db_name)
    print('DSN:', dsn)
    db = cx_Oracle.connect(user=run_db.db_username, password=run_db.db_password, dsn=dsn, encoding='UTF-8')
    print('数据库连接成功')
    print('执行SQL：', task.exec_sql)
    print('告警条件：', task.sql_alert)
    cursor = db.cursor()
    cursor.execute(task.exec_sql)
    query_res = cursor.fetchall()
    title = [i[0] for i in cursor.description]
    result = []
    for res in query_res:
        tmp_dict = {}
        for i in range(0, len(title)):
            tmp_dict[title[i]] = res[i]
        result.append(tmp_dict)
    # print(result)
    if task.sql_alert and len(task.sql_alert.strip()) > 0:
        exec(alert_str.format(task.sql_alert))
    db.close()
    return result


def mysql_exec(task):
    run_db = task.run_db
    db = None
    try:
        db = pymysql.connect(user=run_db.db_username, password=run_db.db_password,
                             host=run_db.db_host, port=run_db.db_port,
                             db=run_db.db_name, charset='utf8')
        print('数据库连接成功')
        print('执行SQL：', task.exec_sql)
        print('告警条件：', task.sql_alert)
        cursor = db.cursor()
        cursor.execute(task.exec_sql)
        query_res = cursor.fetchall()
        title = [i[0] for i in cursor.description]
        result = []
        for res in query_res:
            tmp_dict = {}
            for i in range(0, len(title)):
                tmp_dict[title[i]] = res[i]
            result.append(tmp_dict)
        # print(result)
        if task.sql_alert and len(task.sql_alert.strip()) > 0:
            exec(alert_str.format(task.sql_alert))
        return result
    except Exception as e:
        print(repr(e))
        raise e
    finally:
        print('关闭数据库连接')
        if db:
            db.close()


def redis_exec(task):
    run_db = task.run_db
    r = redis.Redis(host=run_db.db_host, port=run_db.db_port, password=run_db.db_password,
                    db=eval(run_db.db_name))
    info = r.info()
    print(info['used_memory'])
    return info['used_memory']


def alert_fun():
    print('告警函数！触发告警条件！')


task_require_param = ['task_name', 'task_type', 'enabled', 'one_off', 'schedule_type']
exec_sql_param = ['run_db', 'exec_sql']
check_api_param = ['check_api', 'api_method']


def task_param_check(req):
    # 检查任务基础参数
    for key in task_require_param:
        val = req.get(key, None)
        if val is None:
            raise ValueError('缺少参数：' + key)
        if not val or not val.strip():
            raise ValueError('传入参数' + key + '存在空值')
    # 检查定时策略
    schedule_type = req['schedule_type']
    schedule_obj = req.get(schedule_type, None)
    if schedule_obj is None:
        raise ValueError('缺少参数：' + schedule_type)
    if not schedule_obj or not schedule_obj.strip():
        raise ValueError('传入参数' + schedule_type + '存在空值')
    if schedule_type == 'clocked':
        one_off = req.get('one_off', None)
        if one_off is None or one_off == 'false':
            raise ValueError('Clocked定时必须为一次性任务')
    # 检查SQL任务基础参数
    if 'SQL' in req['task_type']:
        for key in exec_sql_param:
            val = req.get(key, None)
            if val is None:
                raise ValueError('缺少参数' + key)
            if not val or not val.strip():
                raise ValueError('传入参数' + key + '存在空值')
        stmts = sqlparse.split(req['exec_sql'])
        if len(stmts) > 1:
            raise ValueError('SQL语句大于1')
    # 检查接口任务基础参数
    if '接口' in req['task_type']:
        for key in check_api_param:
            val = req.get(key, None)
            if val is None:
                raise ValueError('缺少参数' + key)
            if not val or not val.strip():
                raise ValueError('传入参数' + key + '存在空值')
        # JSON格式校验
        if req.get('api_header', None) and len(req['api_header'].strip()) > 0:
            try:
                json.loads(req['api_header'])
            except Exception as e:
                raise ValueError('参数api_header不符合JSON格式:' + repr(e))
        if req.get('api_params', None) and len(req['api_params'].strip()) > 0:
            try:
                json.loads(req['api_params'])
            except Exception as e:
                raise ValueError('参数api_params不符合JSON格式:' + repr(e))
