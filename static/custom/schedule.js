/*** 加载完成标志 ***/
var support_task_init_flag = false
var db_init_flag = false
var api_init_flag = false
var timezone_init_flag = false
var crontab_init_flag = false
var interval_init_flag = false
var clocked_init_flag = false
var wait_time = 0

// 定时器函数
function InitComplete() {
    if (support_task_init_flag && db_init_flag && api_init_flag && timezone_init_flag && crontab_init_flag && interval_init_flag && clocked_init_flag) {
        console.log('数据初始化完毕！' + wait_time)
        Init_task()
    } else {
        if (wait_time >= 3000) {
            alert('数据加载超时！')
        } else {
            wait_time += 50
            setTimeout(InitComplete, 50);//定时操作，100ms之后再执行这个函数.
        }
    }
}


$(function () {
    console.log('页面交互初始化')
    $('.task-ext-info').hide()
    $('.schedule').hide()
    var schedule_type = $('#id_schedule_type').val()
    if (schedule_type != '') {
        $('#' + schedule_type).show()
    }

    $('#id_schedule_type').change(function () {
        $('.schedule').hide()
        var schedule_type = $('#id_schedule_type').val()
        if (schedule_type != '') {
            $('#' + schedule_type).show()
            $('#id_edit_' + schedule_type).show()
            if (schedule_type == 'clocked') {
                $('#id_one_off').attr('checked', true)
            } else {
                $('#id_one_off').attr('checked', false)
            }
        }
    })

    $('#id_edit_crontab').hide()
    $('#id_crontab').change(function () {
        if ($('#id_crontab').val() == '') {
            $('#id_edit_crontab').hide()
        } else {
            $('#id_edit_crontab').show()
        }
    })
    $('#id_edit_interval').hide()
    $('#id_interval').change(function () {
        if ($('#id_interval').val() == '') {
            $('#id_edit_interval').hide()
        } else {
            $('#id_edit_interval').show()
        }
    })
    $('#id_edit_clocked').hide()
    $('#id_clocked').change(function () {
        if ($('#id_clocked').val() == '') {
            $('#id_edit_clocked').hide()
        } else {
            $('#id_edit_clocked').show()
        }
    })

    $('#id_task_type').change(function () {
            $('.task-ext-info').hide()
            if ($('#id_task_type').val().indexOf('SQL') != -1) {
                console.log('SQL')
                $('.exec-sql').show()
            } else if ($('#id_task_type').val().indexOf('接口') != -1) {
                console.log('API')
                $('.api-check').show()
            } else {
                // 其他任务
            }
        }
    )
});

/*** 页面初始化函数 start ***/
function Init_show() {
    $('.task-ext-info').hide()
    $('.schedule').hide()
    var schedule_type = $('#id_schedule_type').val()
    console.log(schedule_type)
    if (schedule_type != '') {
        $('#' + schedule_type).show()
        if ($('#id_' + schedule_type).val() == '') {
            $('#id_edit_' + schedule_type).hide()
        } else {
            $('#id_edit_' + schedule_type).show()
        }
    }

    if ($('#id_task_type').val().indexOf('SQL') != -1) {
        console.log('SQL')
        $('.exec-sql').show()
    } else if ($('#id_task_type').val().indexOf('接口') != -1) {
        console.log('API')
        $('.api-check').show()
    } else {
        // 其他任务
    }
}

function Init_task() {
    var path = window.location.pathname.split('/').filter(item => item != '');
    var task_add = path[path.length - 1] == 'add'
    if (!task_add) {
        var task_id = path[path.length - 2]
        var task_url = '/schedule/task/' + task_id
        $.ajax({
            url: task_url,
            type: "GET",
            success: function (data) {
                console.log(data)
                if (data.code == 0) {
                    var _data = data.task_info
                    $('#id_task_name').val(_data.task.name)
                    $('#id_task_type').val(_data.task.task)
                    $('#id_enabled').attr('checked', _data.task.enabled)
                    $('#id_one_off').attr('checked', _data.task.one_off)
                    $('#id_description').val(_data.task.description)
                    $('#id_start_time').val(_data.task.start_time.replace('T', ' '))
                    if (_data.task.crontab) {
                        $('#id_crontab').val(_data.task.crontab)
                        $('#id_schedule_type').val('crontab')
                    }
                    if (_data.task.interval) {
                        $('#id_interval').val(_data.task.interval)
                        $('#id_schedule_type').val('interval')
                    }
                    if (_data.task.clocked) {
                        $('#id_clocked').val(_data.task.clocked)
                        $('#id_schedule_type').val('clocked')
                    }
                    $('#id_run_db').val(_data.run_db)
                    $('#id_exec_sql').val(_data.exec_sql)
                    $('#id_sql_alert').val(_data.sql_alert)
                    $('#id_check_api').val(_data.check_api)
                    $('#id_api_method').val(_data.api_method)
                    $('#id_api_header').val(_data.api_header)
                    $('#id_api_params').val(_data.api_params)
                    $('#id_api_alert').val(_data.api_alert)
                    Init_show()
                } else {
                    alert(data.msg)
                }

            }
        })
    } else {
        Init_show()
    }
}

function Init_support_task() {
    var sup_url = '/schedule/support_task/';
    $.ajax({
        url: sup_url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.support_task
                $("#id_task_type").empty();
                $.each(_data, function (k, v) {
                    var _option = "<option value='" + v + "'>" + v + "</option>";
                    $("#id_task_type").append(_option);
                });
                // $('#id_task_type').val('测试任务')
                support_task_init_flag = true
            } else {
                alert(data.msg)
            }

        }
    })
}

function Init_db_api() {
    var db_url = '/dbmanager/db_info/';
    $.ajax({
        url: db_url,
        type: "GET",
        success: function (data) {
            if (data.code == 0) {
                var _data = data.dbinfo
                console.log(_data)
                $("#id_run_db").empty();
                $.each(_data, function (k, v) {
                    var _option = "<option value='" + v.pk + "'>" + v.db_nickname + "</option>";
                    $("#id_run_db").append(_option);
                });
                db_init_flag = true
            } else {
                alert(data.msg)
            }

        }
    })

    var api_url = '/apimanager/api_info/'
    $.ajax({
        url: api_url,
        type: "GET",
        success: function (data) {
            if (data.code == 0) {
                var _data = data.apiinfo
                $("#id_check_api").empty();
                $.each(_data, function (k, v) {
                    var _option = "<option value='" + v.pk + "'>" + v.api_nickname + "</option>";
                    $("#id_check_api").append(_option);
                });
                api_init_flag = true
            } else {
                alert(data.msg)
            }
        }
    })
}

function Init_timezones() {
    var timezone_url = '/schedule/timezones/';
    $.ajax({
        url: timezone_url,
        type: "GET",
        success: function (data) {
            if (data.code == 0) {
                var _data = data.timezones
                $("#id_timezone").empty();
                $.each(_data, function (k, v) {
                    var _option = "<option value='" + v + "'>" + v + "</option>";
                    $("#id_timezone").append(_option);
                });
                timezone_init_flag = true
            } else {
                alert(data.msg)
            }

        }
    })
}

/*** 页面初始化函数 end ***/

/*** 任务增删改 start ***/
function post_task() {
    var task_url = '/schedule/task/'
    var token = $("input[name='csrfmiddlewaretoken']").val()
    var path = window.location.pathname.split('/').filter(item => item != '');
    var task_add = path[path.length - 1] == 'add'
    if (!task_add) {
        // 修改
        var task_id = path[path.length - 2]
        task_url += task_id
    }
    var params = {
        "task_name": $('#id_task_name').val(),
        "task_type": $('#id_task_type').val(),
        "enabled": $('#id_enabled').prop('checked'),
        "one_off": $('#id_one_off').prop('checked'),
        "description": $('#id_description').val(),
        "start_time": $('#id_start_time').val(),
        "schedule_type": $('#id_schedule_type').val(),
        "crontab": $('#id_crontab').val(),
        "interval": $('#id_interval').val(),
        "clocked": $('#id_clocked').val(),
        "run_db": $('#id_run_db').val(),
        "exec_sql": $('#id_exec_sql').val(),
        "sql_alert": $('#id_sql_alert').val(),
        "check_api": $('#id_check_api').val(),
        "api_method": $('#id_api_method').val(),
        "api_header": $('#id_api_header').val(),
        "api_params": $('#id_api_params').val(),
        "api_alert": $('#id_api_alert').val(),
    }
    $.ajax({
        url: task_url,
        type: "POST",
        headers: {'X-CSRFToken': token},
        data: params,
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                prev()
            } else {
                alert(data.msg)
            }
        }
    })
}

function delete_schedule() {
    var delete_url = '/schedule/task/delete/'
    var token = $("input[name='csrfmiddlewaretoken']").val()
    var path = window.location.pathname.split('/').filter(item => item != '');
    var task_change = path[path.length - 1] == 'change'
    if (task_change) {
        // 修改
        var task_id = path[path.length - 2]
        $.ajax({
            url: delete_url,
            type: "POST",
            headers: {'X-CSRFToken': token},
            data: {"s_id": task_id},
            success: function (data) {
                console.log(data)
                if (data.code == 0) {
                    prev()
                } else {
                    alert(data.msg)
                }
            }
        })
    }
}


/*** 任务增删改 end ***/

/*** crontab增改查 start ***/
function post_crontab() {
    var url = '/schedule/crontab/'
    if (!$('#id_crontab_add').prop('checked')) {
        url += $('#id_crontab').val()
    }
    console.log(url)
    var token = $("input[name='csrfmiddlewaretoken']").val()
    console.log(token)
    var params = {
        "minute": $('#id_minute').val(),
        "hour": $('#id_hour').val(),
        "day_of_week": $('#id_week').val(),
        "day_of_month": $('#id_day').val(),
        "month_of_year": $('#id_month').val(),
        "timezone": $('#id_timezone').val()
    }
    console.log(params)
    $.ajax({
        url: url,
        type: "POST",
        headers: {'X-CSRFToken': token},
        data: params,
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                Init_crontabs(data.crontab.id)
            } else {
                alert(data.msg)
            }
        }
    })
    $('#crontabModal').modal('hide')
}

function edit_crontab() {
    $('#crontabModalLabel').html('修改Crontab表达式')
    $('#id_crontab_add').attr("checked", false)
    var crontab_id = $('#id_crontab').val()
    var url = '/schedule/crontab/' + crontab_id;
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.crontab
                $('#id_minute').val(_data.minute)
                $('#id_hour').val(_data.hour)
                $('#id_week').val(_data.day_of_week)
                $('#id_day').val(_data.day_of_month)
                $('#id_month').val(_data.month_of_year)
                $('#id_timezone').val(_data.timezone)
            } else {
                alert(data.msg)
            }
        }
    })
}

function add_crontab() {
    $('#crontabModalLabel').html('添加Crontab表达式')
    $('#id_crontab_add').attr("checked", true)
    $('#id_minute').val('')
    $('#id_hour').val('')
    $('#id_week').val('')
    $('#id_day').val('')
    $('#id_month').val('')
    $('#id_timezone').val('Asia/Shanghai')
}

function Init_crontabs(set_val) {
    var url = '/schedule/crontab/';
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.crontab
                $("#id_crontab").empty();
                $.each(_data, function (k, v) {
                    var fields = v.fields
                    var _cont = [fields.minute, fields.hour, fields.day_of_month, fields.month_of_year, fields.day_of_week,];
                    var _option = "<option value='" + v.pk + "'>" + _cont.join(' ') + " (分/时/日/月/周) " + fields.timezone + "</option>";
                    $("#id_crontab").append(_option);
                });
                $("#id_crontab").val(set_val)
                crontab_init_flag = true
            } else {
                alert(data.msg)
            }

        }
    })
}

/*** crontab增改查 end  ***/


/*** interval增改查 start ***/
function post_interval() {
    var url = '/schedule/interval/'
    if (!$('#id_interval_add').prop('checked')) {
        url += $('#id_interval').val();
    }
    console.log(url)
    var token = $("input[name='csrfmiddlewaretoken']").val()
    console.log(token)
    var params = {
        "every": $('#id_every').val(),
        "period": $('#id_period').val(),
    }
    console.log(params)
    $.ajax({
        url: url,
        type: "POST",
        headers: {'X-CSRFToken': token},
        data: params,
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                Init_interval(data.interval.id)
            } else {
                alert(data.msg)
            }
        }
    })
    $('#intervalModal').modal('hide')
}

function edit_interval() {
    $('#intervalModalLabel').html('修改时间间隔')
    $('#id_interval_add').attr("checked", false)
    var interval_id = $('#id_interval').val()
    var url = '/schedule/interval/' + interval_id;
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.interval
                $('#id_every').val(_data.every)
                $('#id_period').val(_data.period)
            } else {
                alert(data.msg)
            }
        }
    })
}

function add_interval() {
    $('#intervalModalLabel').html('添加时间间隔')
    $('#id_interval_add').attr("checked", true)
    $('#id_every').val('')
    $('#id_period').val('')
}

function Init_interval(set_val) {
    var url = '/schedule/interval/';
    var chinese = {
        "days": "天",
        "hours": "小时",
        "minutes": "分钟",
        "seconds": "秒",
        "microseconds": "微秒",
    }
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.interval
                $("#id_interval").empty();
                $.each(_data, function (k, v) {
                    var fields = v.fields
                    var _option = "<option value='" + v.pk + "'>每 " + fields.every + " " + chinese[fields.period] + "</option>";
                    $("#id_interval").append(_option);
                });
                $("#id_interval").val(set_val)
                interval_init_flag = true
            } else {
                alert(data.msg)
            }
        }
    })
}

/*** interval增改查 end ***/

/*** clocked增改查 start ***/
function post_clocked() {
    var url = '/schedule/clocked/'
    if (!$('#id_clocked_add').prop('checked')) {
        url += $('#id_clocked').val();
    }
    console.log(url)
    var token = $("input[name='csrfmiddlewaretoken']").val()
    console.log(token)
    var params = {
        "clocked_time": $('#id_clocked_time').val(),
    }
    console.log(params)
    $.ajax({
        url: url,
        type: "POST",
        headers: {'X-CSRFToken': token},
        data: params,
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                Init_clocked(data.clocked.id)
            } else {
                alert(data.msg)
            }
        }
    })
    $('#clockedModal').modal('hide')
}

function edit_clocked() {
    $('#clockedModalLabel').html('修改指定时间')
    $('#id_clocked_add').attr("checked", false)
    var clocked_id = $('#id_clocked').val()
    var url = '/schedule/clocked/' + clocked_id;
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.clocked
                $('#id_clocked_time').val(_data.clocked_time.replace('T', ' '))
            } else {
                alert(data.msg)
            }
        }
    })
}

function add_clocked() {
    $('#clockedModalLabel').html('添加时间间隔')
    $('#id_clocked_add').attr("checked", true)
    $('#id_clocked_time').val('')
}

function Init_clocked(set_val) {
    var url = '/schedule/clocked/';
    $.ajax({
        url: url,
        type: "GET",
        success: function (data) {
            console.log(data)
            if (data.code == 0) {
                var _data = data.clocked
                $("#id_clocked").empty();
                $.each(_data, function (k, v) {
                    var fields = v.fields
                    var _option = "<option value='" + v.pk + "'>" + fields.clocked_time.replace('T', ' ') + "</option>";
                    $("#id_clocked").append(_option);
                });
                $("#id_clocked").val(set_val)
                clocked_init_flag = true
            } else {
                alert(data.msg)
            }
        }
    })
}

/*** clocked增改查 end ***/