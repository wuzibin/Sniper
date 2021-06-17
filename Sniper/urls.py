"""Sniper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views import static
from django.conf import settings
from django.conf.urls import url
from django.urls import path
from dbmanager.views import db_info
from apimanager.views import api_info
from schedule.views import crontab_timezone, crontab_schedule, crontab_by_id
from schedule.views import interval_schedule, interval_by_id
from schedule.views import clocked_schedule, clocked_by_id
from schedule.views import schedule_by_id, support_task, add_schedule

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    path('schedule/timezones/', crontab_timezone),
    path('schedule/task/', add_schedule),
    path('schedule/task/<int:task_id>', schedule_by_id),
    path('dbmanager/db_info/', db_info),
    path('apimanager/api_info/', api_info),
    path('schedule/support_task/', support_task),
    # crontab
    path('schedule/crontab/', crontab_schedule),
    path('schedule/crontab/<int:crontab_id>', crontab_by_id),
    # interval
    path('schedule/interval/', interval_schedule),
    path('schedule/interval/<int:interval_id>', interval_by_id),
    # clocked
    path('schedule/clocked/', clocked_schedule),
    path('schedule/clocked/<int:clocked_id>', clocked_by_id),
]
