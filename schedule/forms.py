from __future__ import absolute_import, unicode_literals
from django import forms

from django_celery_beat.models import CrontabSchedule


class CrontabScheduleForm(forms.ModelForm):
    class Meta:
        model = CrontabSchedule
        fields = '__all__'
