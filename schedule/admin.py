from django.contrib import admin
from django.utils.html import format_html

from .models import ScheduleExtInfo
from django_celery_beat.models import cronexp, PeriodicTasks
from celery import current_app
from kombu.utils.json import loads
from datetime import timedelta
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy


@admin.register(ScheduleExtInfo)
class ScheduleInfoDisplay(admin.ModelAdmin):
    celery_app = current_app

    list_display = ['get_schedule_name', 'get_schedule_id', 'get_schedule_enabled',
                    'get_timing_strategy', 'get_task_type', 'get_ass_target',
                    'get_last_run_time', 'get_one_off_task']
    search_fields = ['schedule_task__name']
    list_display_links = ['get_schedule_name']
    list_filter = ['schedule_task__enabled']
    actions = ['delete_selected', 'enable_tasks_button', 'disable_tasks_button', 'run_tasks_button']
    show_save_as_new = False
    show_save_and_add_another = False

    '''
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    '''

    # TODO ListFilter重写

    def delete_selected(self, request, queryset):
        opts = self.model._meta
        app_label = opts.app_label

        # Populate deletable_objects, a data structure of all related objects that
        # will also be deleted.
        deletable_objects, model_count, perms_needed, protected = self.get_deleted_objects(queryset, request)

        # The user has already confirmed the deletion.
        # Do the deletion and return None to display the change list view again.
        if request.POST.get('post') and not protected:
            if perms_needed:
                raise PermissionDenied
            n = queryset.count()
            if n:
                for obj in queryset:
                    obj_display = str(obj)
                    self.log_deletion(request, obj, obj_display)
                    obj.delete()
                self.message_user(request, _("Successfully deleted %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(self.opts, n)
                }, messages.SUCCESS)
            # Return None to display the change list page again.
            return None

        objects_name = model_ngettext(queryset)

        if perms_needed or protected:
            title = _("Cannot delete %(name)s") % {"name": objects_name}
        else:
            title = _("Are you sure?")

        context = {
            **self.admin_site.each_context(request),
            'title': title,
            'objects_name': str(objects_name),
            'deletable_objects': [deletable_objects],
            'model_count': dict(model_count).items(),
            'queryset': queryset,
            'perms_lacking': perms_needed,
            'protected': protected,
            'opts': opts,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
            'media': self.media,
        }

        request.current_app = self.admin_site.name

        # Display the confirmation page
        return TemplateResponse(request, self.delete_selected_confirmation_template or [
            "admin/%s/%s/delete_selected_confirmation.html" % (app_label, opts.model_name),
            "admin/%s/delete_selected_confirmation.html" % app_label,
            "admin/delete_selected_confirmation.html"
        ], context)

    def get_schedule_id(self, obj):
        return obj.schedule_task.id

    get_schedule_id.short_description = '内部序号'

    def get_schedule_name(self, obj):
        return obj.schedule_task.name

    get_schedule_name.short_description = '任务名称'

    def get_schedule_enabled(self, obj):
        img_str = '<img src="{}" alt="{}">'
        if obj.schedule_task.enabled:
            return format_html(img_str, '/static/admin/img/icon-yes.svg', 'True')
        return format_html(img_str, '/static/admin/img/icon-no.svg', 'False')

    get_schedule_enabled.short_description = '启用'

    def get_timing_strategy(self, obj):
        if obj.schedule_task.interval:
            return obj.schedule_task.interval
        if obj.schedule_task.crontab:
            return '{0} {1} {2} {3} {4} (m/h/dM/MY/d)'.format(
                cronexp(obj.schedule_task.crontab.minute), cronexp(obj.schedule_task.crontab.hour),
                cronexp(obj.schedule_task.crontab.day_of_month), cronexp(obj.schedule_task.crontab.month_of_year),
                cronexp(obj.schedule_task.crontab.day_of_week))
        if obj.schedule_task.solar:
            return obj.schedule_task.solar
        if obj.schedule_task.clocked:
            return obj.schedule_task.clocked
        return obj.schedule_task.name

    get_timing_strategy.short_description = '定时策略'

    def get_task_type(self, obj):
        return obj.schedule_task.task

    get_task_type.short_description = '任务类型'

    def get_ass_target(self, obj):
        if obj.schedule_task.task == '执行SQL':
            return obj.run_db
        if obj.schedule_task.task == '接口检测':
            return obj.check_api
        return None

    get_ass_target.short_description = '关联目标'

    def get_last_run_time(self, obj):
        time_last = obj.schedule_task.last_run_at
        if time_last:
            return time_last + timedelta(hours=+8)
        return time_last

    get_last_run_time.short_description = '上次运行'

    def get_one_off_task(self, obj):
        img_str = '<img src="{}" alt="{}">'
        if obj.schedule_task.one_off:
            return format_html(img_str, '/static/admin/img/icon-yes.svg', 'True')
        return format_html(img_str, '/static/admin/img/icon-no.svg', 'False')

    get_one_off_task.short_description = '一次性任务'

    # action定义开始

    def enable_tasks_button(self, request, queryset):
        for obj in queryset:
            obj.schedule_task.enabled = True
            obj.schedule_task.save()
        PeriodicTasks.update_changed()
        self.message_user(request, '{0} 个任务已成功{1}'.format(len(queryset), '启用'), level=messages.SUCCESS)

    enable_tasks_button.short_description = '启用任务'
    enable_tasks_button.icon = 'el-icon-check'
    enable_tasks_button.type = 'success'

    def disable_tasks_button(self, request, queryset):
        for obj in queryset:
            obj.schedule_task.enabled = False
            obj.schedule_task.save()
        PeriodicTasks.update_changed()
        # self._message_user_about_update(request, len(queryset), '停用')
        print(request)
        self.message_user(request, '{0} 个任务已成功{1}'.format(len(queryset), '停用'), level=messages.SUCCESS)

    disable_tasks_button.short_description = '停用任务'
    disable_tasks_button.icon = 'el-icon-close'
    disable_tasks_button.type = 'info'

    def run_tasks_button(self, request, queryset):
        self.celery_app.loader.import_default_modules()
        tasks = [(self.celery_app.tasks.get(obj.schedule_task.task),
                  loads(obj.schedule_task.args),
                  loads(obj.schedule_task.kwargs),
                  obj.schedule_task.queue)
                 for obj in queryset]

        if any(t[0] is None for t in tasks):
            for i, t in enumerate(tasks):
                if t[0] is None:
                    break
            not_found_task_name = queryset[i].schedule_task.task
            self.message_user(request, '任务 "{0}" 不存在'.format(not_found_task_name), level=messages.ERROR, )
            return

        task_ids = [task.apply_async(args=args, kwargs=kwargs, queue=queue)
                    if queue and len(queue)
                    else task.apply_async(args=args, kwargs=kwargs)
                    for task, args, kwargs, queue in tasks]
        tasks_run = len(task_ids)
        self.message_user(request, '{0} 个任务已成功运行'.format(tasks_run), level=messages.SUCCESS)

    run_tasks_button.short_description = '运行任务'
    run_tasks_button.icon = 'el-icon-caret-right'
    run_tasks_button.type = 'warning'

    # admin.site.register(ScheduleExtInfo)
